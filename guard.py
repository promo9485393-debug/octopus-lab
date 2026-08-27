# -*- coding: utf-8 -*-
"""
ПРИВАТНЫЙ ГАРД ПЕРЕД ПУБЛИКАЦИЕЙ. Запускать ДО каждого деплоя.

На GitHub Pages такая проверка была в deploy.ps1. При переезде на Vercel её легко
потерять — и тогда личные позиции уедут в публикацию молча. Здесь она отдельным
файлом, который падает с ненулевым кодом, а не печатает предупреждение.

Проверяется три вещи:
  1) маркер личного блока (U+1F4BC) — он не должен встречаться нигде;
  2) слова, которыми описываются ЛИЧНЫЕ входы («мой вход», «моя средняя», «у меня»);
  3) тикеры личных позиций рядом с числами объёма — ORCU и подобное.

Проверка на «пустой результат»: гард сам себя тестирует на подделанном файле,
иначе «ничего не нашли» неотличимо от «не искали».

  python site/guard.py            проверить site/
  python site/guard.py --selftest убедиться, что гард вообще способен ловить
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = chr(0x1F4BC)                      # 💼 — подпись запрещённого личного блока
PHRASES = ["мой вход", "моя средняя", "мои позиции", "у меня в позиции",
           "личная позиция", "личные позиции", "личный портфель"]
PRIVATE_TICKERS = ["ORCU"]


def scan_text(name, text):
    hits = []
    if MARKER in text:
        hits.append("%s: найден маркер личного блока U+1F4BC" % name)
    low = text.lower()
    for p in PHRASES:
        # Границы слов обязательны: «пуб-ЛИЧНЫЙ ПОРТФЕЛЬ» содержит «личный портфель»
        # подстрокой, и без  гард отменял публикацию собственного README.
        # Гард, который кричит на ровном месте, рано или поздно отключают —
        # и тогда он не защищает уже ничего.
        if re.search(r"(?<![\w-])" + re.escape(p).replace(r"\ ", r"\s+") + r"(?![\w-])", low):
            hits.append("%s: фраза о личной позиции — «%s»" % (name, p))
    for t in PRIVATE_TICKERS:
        if re.search(r"\b%s\b" % t, text):
            hits.append("%s: тикер личной позиции — %s" % (name, t))
    return hits


def scan_dir(d):
    hits, checked = [], []
    for root, _, files in os.walk(d):
        if ".git" in root or "node_modules" in root:
            continue
        for f in files:
            if not f.lower().endswith((".html", ".json", ".js", ".css", ".md", ".txt")):
                continue
            p = os.path.join(root, f)
            if os.path.basename(p) == "guard.py":
                continue
            try:
                text = open(p, encoding="utf-8").read()
            except Exception as e:
                hits.append("%s: не прочитан (%r) — публиковать непроверенное нельзя" % (f, e))
                continue
            checked.append(os.path.relpath(p, d))
            hits.extend(scan_text(os.path.relpath(p, d), text))
    return hits, checked


def selftest():
    """Гард обязан ловить подделку. Без этого «чисто» ничего не значит."""
    cases = [("маркер", "текст " + MARKER + " текст"),
             ("фраза", "здесь описан Мой Вход по 25"),
             ("тикер", "держим 5000 ORCU в лотерее")]
    ok = True
    print("САМОПРОВЕРКА ГАРДА")
    for name, text in cases:
        h = scan_text("тест", text)
        print("  %-8s -> %s" % (name, "поймал" if h else "❌ ПРОПУСТИЛ"))
        ok &= bool(h)
    for name, text in (("чистый", "обычный текст про пробой 20 дней"),
                       ("пуб-личный", "данные: trades.json (публичный портфель)"),
                       ("наличные", "наличные на счету и обезличенные данные")):
        c = scan_text("тест", text)
        print("  %-10s -> %s" % (name, "молчит (верно)" if not c else "❌ ЛОЖНОЕ: %s" % c[0]))
        ok &= not c
    print("итог: %s" % ("гард работоспособен" if ok else "ГАРД СЛОМАН, публиковать нельзя"))
    return ok


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if not selftest():
        print("\n❌ гард не прошёл самопроверку — деплой отменён")
        sys.exit(1)
    hits, checked = scan_dir(HERE)
    print("\nПРОВЕРКА ПУБЛИКУЕМЫХ ФАЙЛОВ (%d шт)" % len(checked))
    for c in checked:
        print("   %s" % c)
    if not checked:
        print("❌ не проверено НИ ОДНОГО файла — это не «чисто», это сломанная проверка")
        sys.exit(1)
    if hits:
        print("\n❌ ПУБЛИКАЦИЯ ОТМЕНЕНА, найдено %d:" % len(hits))
        for h in hits:
            print("   %s" % h)
        sys.exit(1)
    print("\n✅ личных данных не найдено — публиковать можно")


if __name__ == "__main__":
    main()
