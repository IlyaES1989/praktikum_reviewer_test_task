import datetime as dt

"""
Общие рекомендации:
- Использовать type hints. Эта привычка повышает читаемость кода 
и упрощает разработку более сложных вещей. Подробнее - https://docs.python.org/3/library/typing.html

"""


class Record:
    def __init__(self, amount, comment, date=''):
        """
        Рекомендации:
        - Формально синтаксис питона допускает такую запись, но лучшее ее использовать
        для простых, коротких выражений типа a+1 if a else b. Проверку значения date лучше вынести
        в отдельный метод.
        Замечания:
        - Для получения объекта datetime.date можно использовать
        dt.date.today() вместо dt.datetime.now().date()

        """
        self.amount = amount
        self.date = (
            dt.datetime.now().date() if
            not
            date else dt.datetime.strptime(date, '%d.%m.%Y').date())
        self.comment = comment


class Calculator:
    def __init__(self, limit):
        self.limit = limit
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_today_stats(self):
        """
        Замечания к форме:
            - PEP8 говорит, что имя переменной должно быть lowercase
                (подробнее https://peps.python.org/pep-0008/#function-and-variable-names)
            -  ранее был описан класс Record, и в области видимости функции get_today_stats
                происходит переопределение класса Record его инстансом.
            - инкрементировать today_stats лучше так:
                         today_stats += Record.amount
        Замечания к сути функции:
            - со временем, self.records может стать очень большим списком и постоянное
                итерирование этого списка, с последующим подсчетом всех записей, относящихся
                к сегодняшней дате (которые, к слову, располагаются в конце списка) будет весьма ресурсоемким.
                Лучше описать отдельным методом инкрементирование счетчика записей, при добавлении новых записей.
            Например:
                1. создаем аттрибут класса record_stats типа defaultdict
                (подробнее - https://docs.python.org/3/library/collections.html#collections.defaultdict:)

                from collections import defaultdict

                class Calculator:
                    record_stats = defaultdict(int)

                2. Создаем метод _update_record_stats, который при каждом вызове будет увеличивать счетчик:

                    def _update_record_stats(self, date: dt.date, amount:int) ->typing.NoReturn:
                        self.record_stats[date] += amount

                3. Добавляем вызов метода _update_record_stats в метод add_record:

                        def add_record(self, record):
                            self.records.append(record)
                            self._update_record_stats(record.date, record.amount)
                4. Изменяем метод get_today_stats:
                        def get_today_stats(self) -> int:
                            return self.record_stats[dt.date.today()]

        """
        today_stats = 0
        for Record in self.records:
            if Record.date == dt.datetime.now().date():
                today_stats = today_stats + Record.amount
        return today_stats

    def get_week_stats(self):
        """
        Замечание:
            - аналогично с get_today_stats - итерирование  self.records будет ресурсоемким.
                Если применить рекомендации данные к get_today_stats, то для расчета недельной статистики
                можно суммировать значения record_stats за определенные даты.
        """
        week_stats = 0
        today = dt.datetime.now().date()
        for record in self.records:
            if (
                (today - record.date).days < 7 and
                (today - record.date).days >= 0
            ):
                week_stats += record.amount
        return week_stats


class CaloriesCalculator(Calculator):
    """
    Рекомендации:
        - inline комментарии используются для пояснения логики определенных строк кода.
            Для комментирования назначения функций и методов лучше использовать docstring
        - можно не использовать оператор else, а также не нужно брать в скобки возвращаемую строку
        Пример:
            if x > 0:
                return f"Сегодня можно съесть что-нибудь" \
                    f" ещё, но с общей калорийностью не более {x} кКал"
            return "Хватит есть!"
    """
    def get_calories_remained(self):  # Получает остаток калорий на сегодня
        x = self.limit - self.get_today_stats()
        if x > 0:
            return f'Сегодня можно съесть что-нибудь' \
                   f' ещё, но с общей калорийностью не более {x} кКал'
        else:
            return('Хватит есть!')


class CashCalculator(Calculator):
    """
    Рекомендации:
        - приведение к типу float аттрибутов класса USD_RATE и EURO_RATE выглядит избыточным.
        Лучше: USD_RATE: float = 60.0

    """
    USD_RATE = float(60)  # Курс доллар США.
    EURO_RATE = float(70)  # Курс Евро.

    def get_today_cash_remained(self, currency,
                                USD_RATE=USD_RATE, EURO_RATE=EURO_RATE):
        """
        Рекомендации:
            - аргументы функций должны быть в lowercase

        Замечания:
            - аттрибуты класса USD_RATE и EURO_RATE - изменяемые (mutable).
                Использование mutable значений в качестве значений по-умолчанию для аргументов
                функций и методов - плохая практика
                (подробнее - https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments_)
            лучше так:
                def get_today_cash_remained(self, currency, usd_rate=None, euro_rate=None):
                    usd_rate = self.USD_RATE if not usd_rate else usd_rate
                    euro_rate = self.EURO_RATE if not euro_rate else euro_rate

            - блок if-elif выглядит запутанно для трех валют.
                Такой код сложно читать, покрывать тестами и вносить в него изменения.
                Посмотри в сторону factory
                (подробнее - https://levelup.gitconnected.com/design-patterns-in-python-factory-pattern-beea1da31c17)

            - если currency_type == 'rub', остаток всегда будет равен 1 руб, должно быть:
                elif currency_type == 'rub':
                    currency_type = 'руб'

            - лучше придерживаться одного стиля в использовании строк. Либо 'На сегодня осталось {:.2f} ',
                либо использовать f-строку и round в блоке cash_remained < 0
        """
        currency_type = currency
        cash_remained = self.limit - self.get_today_stats()
        if currency == 'usd':
            cash_remained /= USD_RATE
            currency_type = 'USD'
        elif currency_type == 'eur':
            cash_remained /= EURO_RATE
            currency_type = 'Euro'
        elif currency_type == 'rub':
            cash_remained == 1.00
            currency_type = 'руб'
        if cash_remained > 0:
            return (
                f'На сегодня осталось {round(cash_remained, 2)} '
                f'{currency_type}'
            )
        elif cash_remained == 0:
            return 'Денег нет, держись'
        elif cash_remained < 0:
            return 'Денег нет, держись:' \
                   ' твой долг - {0:.2f} {1}'.format(-cash_remained,
                                                     currency_type)

    """
    Замечание:
        - метод наследуется от Calculator, повторно его описывать не нужно
    """
    def get_week_stats(self):
        super().get_week_stats()
