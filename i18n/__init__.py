#!/usr/bin/env python3
import os.path

import argostranslate.package
import argostranslate.translate
import polib

DEFAULT_ORIGIN_LOCALE = "en"
DEFAULT_POFILE_METADATA = {
    "Project-Id-Version": "1.0",
    "Report-Msgid-Bugs-To": "support@akatsuki.gg",
    "MIME-Version": "1.0",
    "Content-Type": "text/plain; charset=utf-8",
    "Content-Transfer-Encoding": "8bit",
}

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


def _fetch_or_create_pofile(filepath: str) -> polib.POFile:
    if os.path.exists(filepath):
        pofile = polib.pofile(filepath, check_for_duplicates=True)
    else:
        pofile = polib.POFile(check_for_duplicates=True)
        pofile.metadata = DEFAULT_POFILE_METADATA
        pofile.save(filepath)
    return pofile


def _load_po_dict(
    locale: str,
    origin_locale: str = DEFAULT_ORIGIN_LOCALE,
) -> dict[str, str]:
    pofile_path = f"{BASE_DIR}/{origin_locale}_{locale}.po"
    pofile = _fetch_or_create_pofile(pofile_path)
    return {e.msgid: e.msgstr for e in pofile.translated_entries()}


def _cache_translation(
    text: str,
    translated: str,
    locale: str,
    origin_locale: str = DEFAULT_ORIGIN_LOCALE,
) -> None:
    pofile_path = f"{BASE_DIR}/{origin_locale}_{locale}.po"
    pofile = _fetch_or_create_pofile(pofile_path)
    pofile.append(polib.POEntry(msgid=text, msgstr=translated))
    pofile.save(pofile_path)


def translate_text(
    text: str,
    locale: str,
    origin_locale: str = DEFAULT_ORIGIN_LOCALE,
) -> str:
    """\
    Translate text from an origin_locale to that of a given locale.

    This function will cache translations in a .po file in the BASE_DIR
    directory. If the translation is not found in the cache, it will be
    translated using argostranslate and then cached.
    """
    combination = (origin_locale, locale)
    if combination not in seen_combinations:
        _download_and_install_argos_translate_package(*combination)
        seen_combinations.add(combination)

    translations = _load_po_dict(locale, origin_locale)
    if not (translated := translations.get(text)):
        translated = argostranslate.translate.translate(text, origin_locale, locale)
        _cache_translation(text, translated, locale, origin_locale)

    return translated


if __name__ == "__main__":
    text = "Goodnight world!"
    translated = translate_text(text, "es")
    print(f"Translated {text} to {translated}")
