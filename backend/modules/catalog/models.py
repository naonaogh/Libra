from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class BookCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    BORROWED = "BORROWED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"


book_authors = Table(
    "book_authors",
    Base.metadata,
    Column(
        "book_id",
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "author_id",
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


book_genres = Table(
    "book_genres",
    Base.metadata,
    Column(
        "book_id",
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    isbn: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    publication_year: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors,
        back_populates="books",
    )

    genres: Mapped[list["Genre"]] = relationship(
        secondary=book_genres,
        back_populates="books",
    )

    copies: Mapped[list["BookCopy"]] = relationship(
        back_populates="book",
    )


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="authors",
    )


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    books: Mapped[list["Book"]] = relationship(
        secondary=book_genres,
        back_populates="genres",
    )


class BookCopy(Base):
    __tablename__ = "book_copies"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey(
            "books.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    inventory_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    status: Mapped[BookCopyStatus] = mapped_column(
        SQLEnum(
            BookCopyStatus,
            name="book_copy_status",
        ),
        nullable=False,
        default=BookCopyStatus.AVAILABLE,
        server_default=BookCopyStatus.AVAILABLE.value,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    acquired_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    book: Mapped["Book"] = relationship(
        back_populates="copies",
    )

    __table_args__ = (
        Index(
            "ix_book_copies_book_id",
            "book_id",
        ),
        Index(
            "ix_book_copies_status",
            "status",
        ),
    )