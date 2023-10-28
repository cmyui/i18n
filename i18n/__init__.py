#!/usr/bin/env python3
import os.path

import argostranslate.package
import argostranslate.translate
import polib

DEFAULT_ORIGIN_LOCALE = "en"
BASE_DIR = os.getenv("BASE_DIR", None) or "translations"

seen_combinations: set[tuple[str, str]] = set()


def _download_and_install_argos_translate_package(from_code: str, to_code: str) -> None:
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: (x.from_code, x.to_code) == (from_code, to_code),
            available_packages,
        ),
    )
    argostranslate.package.install_from_path(package_to_install.download())


def i18n_get_text(
    text: str,
    locale: str,
    origin_locale: str = DEFAULT_ORIGIN_LOCALE,
) -> str:
    combination = (origin_locale, locale)
    if combination not in seen_combinations:
        _download_and_install_argos_translate_package(*combination)
        seen_combinations.add(combination)

    pofile_path = f"{BASE_DIR}/{origin_locale}_{locale}.po"
    if os.path.exists(pofile_path):
        pofile = polib.pofile(pofile_path, check_for_duplicates=True)
    else:
        pofile = polib.POFile(check_for_duplicates=True)
        pofile.metadata = {
            "Project-Id-Version": "1.0",
            "Report-Msgid-Bugs-To": "support@akatsuki.gg",
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
        }

    translated = argostranslate.translate.translate(text, origin_locale, locale)
    if text not in [po.msgid for po in pofile.translated_entries()]:
        pofile.append(polib.POEntry(msgid=text, msgstr=translated))
        pofile.save(pofile_path)

    return translated


if __name__ == "__main__":
    text = "Goodnight world!"
    translated = i18n_get_text(text, "es")
    print(f"Translated {text} to {translated}")
