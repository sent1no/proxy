from datetime import datetime, timezone
from sqlalchemy import (Column, Integer, String, Boolean,
                        Float, DateTime, ForeignKey, Table, Text)
from sqlalchemy.orm import relationship
from app.database import Base

# Зв'язок User <-> Role (M:N)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"),
           primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"),
           primary_key=True),
)

# Зв'язок Role <-> Permission (M:N)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"),
           primary_key=True),
    Column("permission_id", Integer,
           ForeignKey("permissions.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Зовнішній ключ на групу (для студентів)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    # ── Зашифровані поля (Практична №7 — Field-Level Encryption) ──
    # У БД зберігається шифротекст Fernet (gAAAAAB...)
    # Доступ через property .email та .phone — прозоре encrypt/decrypt
    _encrypted_email = Column("encrypted_email", String(500),
                               nullable=False, default="")
    _encrypted_phone = Column("encrypted_phone", String(500),
                               nullable=True)

    # ── Property: email (прозоре шифрування) ──

    @property
    def email(self) -> str:
        """Автоматично розшифровує email при читанні."""
        from app.crypto.encryption import decrypt_field
        return decrypt_field(self._encrypted_email)

    @email.setter
    def email(self, value: str):
        """Автоматично шифрує email при записі."""
        from app.crypto.encryption import encrypt_field
        self._encrypted_email = encrypt_field(value)

    # ── Property: phone (прозоре шифрування) ──

    @property
    def phone(self) -> str | None:
        """Автоматично розшифровує телефон при читанні."""
        if not self._encrypted_phone:
            return None
        from app.crypto.encryption import decrypt_field
        return decrypt_field(self._encrypted_phone)

    @phone.setter
    def phone(self, value: str | None):
        """Автоматично шифрує телефон при записі."""
        if value:
            from app.crypto.encryption import encrypt_field
            self._encrypted_phone = encrypt_field(value)
        else:
            self._encrypted_phone = None

    # Зв'язки
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    group = relationship("Group", back_populates="students")
    grades = relationship("Grade", back_populates="student",
                          foreign_keys="Grade.student_id")

    def __repr__(self):
        return f"<User {self.username}>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions,
                               back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    roles = relationship("Role", secondary=role_permissions,
                         back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)

    students = relationship("User", back_populates="group")

    def __repr__(self):
        return f"<Group {self.name}>"


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    credits = Column(Float, nullable=False)
    semester = Column(Integer, nullable=False)

    grades = relationship("Grade", back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    date_assigned = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    student = relationship("User", back_populates="grades",
                           foreign_keys=[student_id])
    subject = relationship("Subject", back_populates="grades")
    teacher = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return (f"<Grade student={self.student_id} "
                f"subject={self.subject_id} "
                f"grade={self.grade}>")


# Практична №8: Журналювання подій та аудит безпеки
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="success")
    details = Column(Text, nullable=True)

    actor = relationship("User", foreign_keys=[actor_user_id])

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.actor_user_id} at {self.timestamp}>"
