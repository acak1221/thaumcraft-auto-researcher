# Contributing to ThaumcraftAutoResearcher

Спасибо за интерес к улучшению проекта! Это руководство поможет вам внести свой вклад в разработку.

## 🚀 Быстрый старт для разработчиков

### 1. Настройка окружения

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd ThaumcraftAutoResearcher

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Установите pre-commit hooks
pre-commit install
```

### 2. Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием кода
pytest --cov=src --cov-report=html

# Запуск только unit тестов
pytest -m "unit"

# Запуск только быстрых тестов
pytest -m "not slow"
```

### 3. Проверка качества кода

```bash
# Форматирование кода
black src/ tests/

# Сортировка импортов
isort src/ tests/

# Проверка стиля
flake8 src/ tests/

# Проверка типов
mypy src/

# Проверка безопасности
bandit -r src/
```

## 📋 Процесс разработки

### 1. Создание веток

```bash
# Для новой функциональности
git checkout -b feature/описание-функциональности

# Для исправления бага
git checkout -b bugfix/описание-бага

# Для улучшения производительности
git checkout -b perf/описание-улучшения
```

### 2. Написание кода

- **Следуйте PEP 8** и используйте `black` для форматирования
- **Добавляйте type hints** ко всем функциям и методам
- **Пишите docstrings** для всех публичных функций
- **Обрабатывайте ошибки** явно, избегайте `except Exception`
- **Используйте логирование** вместо `print()` для отладки

### 3. Тестирование

- **Пишите тесты** для всего нового кода
- **Поддерживайте покрытие** выше 80%
- **Группируйте тесты** по классам и модулям
- **Используйте fixtures** для общих данных тестирования
- **Мокайте внешние зависимости** (файлы, сеть, UI)

### 4. Документация

- **Обновляйте README.md** при изменении API
- **Добавляйте комментарии** к сложной логике
- **Документируйте изменения** в CHANGELOG.md

## 🧪 Стандарты тестирования

### Структура тестов

```python
# tests/test_module_name.py
"""
Tests for module_name module.
"""
import pytest
from unittest.mock import Mock, patch

from src.module_name import function_to_test


class TestFunctionName:
    """Test cases for function_name."""
    
    def test_normal_case(self):
        """Test normal operation."""
        # Arrange
        input_data = "test"
        expected = "expected_result"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case."""
        # Test implementation
        pass
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function_to_test(invalid_input)
```

### Маркировка тестов

```python
@pytest.mark.unit
def test_unit_function():
    """Быстрый unit тест."""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """Тест интеграции между компонентами."""
    pass

@pytest.mark.slow
def test_performance_heavy():
    """Медленный тест производительности."""
    pass
```

## 🏗️ Архитектурные принципы

### 1. SOLID принципы

- **Single Responsibility**: Каждый класс/функция имеет одну ответственность
- **Open/Closed**: Открыт для расширения, закрыт для модификации
- **Liskov Substitution**: Подклассы должны заменять базовые классы
- **Interface Segregation**: Множество специфических интерфейсов лучше одного общего
- **Dependency Inversion**: Зависимости от абстракций, не от конкретных реализаций

### 2. Паттерны проектирования

- **Observer** для событий UI
- **Strategy** для различных алгоритмов
- **Factory** для создания объектов
- **Singleton** только там, где действительно нужен (кэши, логгеры)

### 3. Обработка ошибок

```python
# ✅ Хорошо
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    raise
except AnotherException as e:
    logger.warning(f"Alternative path: {e}")
    return default_value

# ❌ Плохо
try:
    result = risky_operation()
except Exception as e:
    pass  # Молчаливое игнорирование ошибок
```

## 📊 Производительность

### 1. Профилирование

```bash
# Профилирование памяти
python -m memory_profiler script.py

# Профилирование времени выполнения
python -m line_profiler script.py
```

### 2. Оптимизация

- **Используйте кэширование** для дорогих операций
- **Ограничивайте размеры коллекций** для предотвращения утечек памяти
- **Используйте ленивые вычисления** где возможно
- **Оптимизируйте работу с изображениями** (кэш, сжатие)

## 🔒 Безопасность

### 1. Проверки безопасности

```bash
# Проверка уязвимостей в зависимостях
safety check

# Проверка кода на уязвимости
bandit -r src/
```

### 2. Принципы безопасности

- **Валидируйте все входные данные**
- **Используйте безопасные пути к файлам**
- **Не логируйте конфиденциальную информацию**
- **Ограничивайте права доступа**

## 📝 Процесс ревью

### 1. Чек-лист для Pull Request

- [ ] Все тесты проходят
- [ ] Код отформатирован (black, isort)
- [ ] Нет предупреждений линтера
- [ ] Покрытие тестами не уменьшилось
- [ ] Документация обновлена
- [ ] Добавлены type hints
- [ ] Обработаны ошибки
- [ ] Нет конфиденциальной информации в коде

### 2. Описание Pull Request

```markdown
## Описание изменений
Краткое описание того, что изменено и зачем.

## Тип изменений
- [ ] Исправление бага
- [ ] Новая функциональность
- [ ] Критическое изменение (breaking change)
- [ ] Улучшение документации

## Тестирование
- [ ] Добавлены новые тесты
- [ ] Все тесты проходят
- [ ] Проверено вручную

## Чек-лист
- [ ] Код отформатирован
- [ ] Нет предупреждений линтера
- [ ] Документация обновлена
```

## 🐛 Отчеты об ошибках

### Шаблон Issue

```markdown
**Описание бага**
Краткое описание проблемы.

**Воспроизведение**
Шаги для воспроизведения:
1. Откройте '...'
2. Кликните на '...'
3. Ошибка появляется

**Ожидаемое поведение**
Что должно было произойти.

**Скриншоты/Логи**
Если применимо, добавьте скриншоты или логи.

**Окружение:**
- ОС: [Windows/Linux/macOS]
- Python версия: [3.8/3.9/3.10/3.11]
- Версия проекта: [1.0.0]

**Дополнительная информация**
Любая другая полезная информация.
```

## 📚 Полезные ресурсы

- [PEP 8 - Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Clean Code Principles](https://clean-code-developer.com/)

## 🤝 Сообщество

- Будьте уважительны к другим участникам
- Помогайте новичкам
- Делитесь знаниями и опытом
- Следуйте Code of Conduct

## 📞 Контакты

Если у вас есть вопросы, создайте Issue или свяжитесь с мейнтейнерами проекта.