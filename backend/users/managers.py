from django.contrib.auth.models import BaseUserManager


class UserAccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username=None, first_name=None,
                     last_name=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, first_name=None,
                    last_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, first_name,
                                 last_name, password, **extra_fields)

    def create_superuser(self, email, username=None, first_name=None,
                         last_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, first_name,
                                 last_name, password, **extra_fields)
