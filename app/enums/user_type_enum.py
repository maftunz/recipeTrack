from typing import Optional
from enum import Enum

class UserType(Enum):
    DOCTOR = "doctor"
    PHARMACIST = "pharmacist"

    def label(self, lang="ru"):
        translations = {
            "doctor": {"ru": "Врач", "uz": "Shifokor", "en": "Doctor"},
            "pharmacist": {"ru": "Фармацевт", "uz": "Farmatsevt", "en": "Pharmacist"},
        }
        return translations.get(self.value, {}).get(lang, self.value)

    @classmethod
    def key_by_label(cls, label: str, lang: str = 'ru') -> Optional[str]:
        translations = {
            "doctor": {"ru": "Врач", "uz": "Shifokor", "en": "Doctor"},
            "pharmacist": {"ru": "Фармацевт", "uz": "Farmatsevt", "en": "Pharmacist"},
        }
        for key, langs in translations.items():
            if langs.get(lang) == label:
                return key
        return None

USER_TYPE_TRANSLATIONS = {
    "doctor": {
        "en": "Doctor",
        "ru": "Доктор",
    },
    "pharmacist": {
        "en": "Pharmacist",
        "ru": "Фармацевт",
    },
}