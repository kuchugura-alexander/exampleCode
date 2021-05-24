from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import binascii


class AbsModel(models.Model):
    """
    Abstract model for all classes.
    """
    created_at = models.DateTimeField(auto_now_add=True,
                                      blank=False, verbose_name="Date Published:", help_text="Дата создания записи.")

    modified_at = models.DateField(auto_now=True,
                                   blank=False, verbose_name="Date Modify:", help_text="Дата последнего изменения.")

    class Meta:
        abstract = True


class Human(AbsModel):
    """
    Main models about human.
    """
    nickname = models.CharField(max_length=200, default="",
                                blank=True, verbose_name="Nickname:", help_text="Псевдоним.")
    phone = PhoneNumberField(default="",
                             blank=True, verbose_name="Phone:", help_text="Номер телефона.")
    email = models.EmailField(max_length=200, default="",
                              blank=True, verbose_name="E-mail:", help_text="E-mail главный.")
    surname = models.CharField(max_length=200, default="",
                               blank=False, verbose_name="Surname:", help_text="Фамилия.")
    name = models.CharField(max_length=200, default="",
                            blank=False, verbose_name="Name:", help_text="Имя.")
    middle_name = models.CharField(max_length=200, default="",
                                   blank=True, verbose_name="Middle name:", help_text="Отчество.")
    gender = models.ForeignKey('Gender', on_delete=models.PROTECT, null=True,
                               related_name='humans', related_query_name='human',
                               blank=False, verbose_name="Gender:", help_text="Пол.")
    city = models.ForeignKey('City', on_delete=models.PROTECT, null=True,
                             related_name='humans', related_query_name='human',
                             blank=False, verbose_name="City:", help_text="Город.")
    level_english = models.ForeignKey('LevelLanguage', on_delete=models.PROTECT, null=True,
                                      related_name='humans', related_query_name='human',
                                      blank=False, verbose_name="Level English:", help_text="Уровень Английского.")
    skills_programming = models.ManyToManyField('SkillProgramming',
                                                related_name='humans', related_query_name='human',
                                                blank=False, verbose_name="Skills:", help_text="Навыки.")
    token = models.CharField(max_length=40, default="",
                             blank=True, verbose_name="Token:", help_text="Токен.")

    def __str__(self):
        return "{0} {1} - {2}".format(self.surname, self.name, self.email)

    class Meta:
        verbose_name = "Человек"
        verbose_name_plural = "Человеки"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = binascii.hexlify(os.urandom(20)).decode()
        super().save(*args, **kwargs)

####################################################################################


class Gender(AbsModel):
    """
    Gender: male, female and others.
    """
    gender = models.CharField(max_length=100, default="",
                              blank=False, verbose_name="Gender:", help_text="Пол.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0}".format(self.gender)

    class Meta:
        verbose_name = "Пол"
        verbose_name_plural = "Полы"


####################################################################################


class City(AbsModel):
    """
    Current city. (with Country and TimeZone)
    """
    title = models.CharField(max_length=50, default="",
                             blank=False, verbose_name="City:", help_text="Город.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")
    country = models.ForeignKey('Country', on_delete=models.PROTECT, null=True,
                                related_name='cities', related_query_name='city',
                                blank=True, verbose_name="Country:", help_text="Страна.")
    timezone = models.ForeignKey('TimeZoneResidence', on_delete=models.PROTECT, null=True,
                                 related_name='cities', related_query_name='city',
                                 blank=True, verbose_name="Time Zone:", help_text="Временная зона.")

    def __str__(self):
        return "{0} - {1} ({2})".format(self.country, self.title, self.timezone)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class Country(AbsModel):
    """
    Current country. (with TimeZone and Domen)
    """
    domen = models.CharField(max_length=5, default="",
                             blank=False, verbose_name="Domen:", help_text="Домен.")
    title = models.CharField(max_length=50, default="",
                             blank=False, verbose_name="Country:", help_text="Страна.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0} - {1}".format(self.domen, self.title)

    class Meta:
        verbose_name = "Стран"
        verbose_name_plural = "Страны"


class TimeZoneResidence(AbsModel):
    """
    Time zone for binding to city.
    """
    timezone = models.CharField(max_length=100, default="",
                                blank=False, verbose_name="Time Zone:", help_text="Временная зона города.")
    hours = models.IntegerField(default=0,
                                blank=False, verbose_name="Time Zone Hours(+/-):", help_text="Час +/-.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        if self.hours > 0:
            return "{0} : +{1}".format(self.timezone, self.hours)
        else:
            return "{0} : {1}".format(self.timezone, self.hours)

    class Meta:
        verbose_name = "Тайм Зона"
        verbose_name_plural = "Тайм Зоны"


####################################################################################


class LevelLanguage(AbsModel):
    """
    Level Language: Into CERF system, LevelLanguageTitle, LevelLanguageKnowledge.
    """
    CHOICE_CEFR = (
        ('CEFR',    'ДА - В системе'),
        ('NO CEFR', 'НЕТ - Наша оценка'),
    )
    CEFR = models.CharField(max_length=100, default="", choices=CHOICE_CEFR,
                            blank=False, verbose_name="CERF ??:", help_text="Уровень Мировой ил Наша интерпретация.")
    level = models.ForeignKey('LevelLanguageTitle', on_delete=models.PROTECT, null=True,
                              related_name='LevelLanguages', related_query_name='LevelLanguage',
                              blank=False, verbose_name="Level:", help_text="Уровень.")
    knowledge = models.ForeignKey('LevelLanguageKnowledge', on_delete=models.PROTECT, null=True,
                                  related_name='LevelLanguages', related_query_name='LevelLanguage',
                                  blank=False, verbose_name="Knowledge:", help_text="Знание.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0} ({1})".format(self.level, self.knowledge)

    class Meta:
        verbose_name = "Уровень языка"
        verbose_name_plural = "Уровни языков"


class LevelLanguageTitle(AbsModel):
    """
    Title Level Language: A1, B2 and others.
    """
    suffix = models.CharField(max_length=2, default="",
                              blank=True, verbose_name="Suffix:", help_text="Суффикс.")
    title = models.CharField(max_length=100, default="",
                             blank=False, verbose_name="Title:", help_text="Название.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0} - {1}".format(self.suffix, self.title)

    class Meta:
        verbose_name = "Название уровеня языка"
        verbose_name_plural = "Названия уровней языков"


class LevelLanguageKnowledge(AbsModel):
    """
    Knowledge Level Language: BASIC, INDEPENDENT and others.
    """
    title = models.CharField(max_length=100, default="",
                             blank=False, verbose_name="Knowledge:", help_text="Знание.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0}".format(self.title)

    class Meta:
        verbose_name = "Знание уровеня языка"
        verbose_name_plural = "Знание уровней языков"

####################################################################################


class SkillProgramming(AbsModel):
    """
    Skills.
    """
    title = models.CharField(max_length=100, default="",
                             blank=False, verbose_name="Skills:", help_text="Навыки и умения.")
    description = models.TextField(max_length=400, default="",
                                   blank=True, verbose_name="Description:", help_text="Описание.")

    def __str__(self):
        return "{0}".format(self.title)

    class Meta:
        verbose_name = "Дополнительный навык"
        verbose_name_plural = "Дополнительный навыки"
