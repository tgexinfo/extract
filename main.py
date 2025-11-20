import os
import phonenumbers
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Please send me a text file, and I’ll extract all phone numbers using Google’s libphonenumber."
    )

# --- File handler ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("⚠️ Please send a valid text file.")
        return

    # Ensure downloads folder exists
    os.makedirs("downloads", exist_ok=True)

    # Download file locally
    file_path = os.path.join("downloads", document.file_name)
    await document.get_file().download_to_drive(file_path)

    # Read file content
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    total_lines = len(lines)
    extracted_numbers = []

    # Extract numbers globally
    for line in lines:
        for match in phonenumbers.PhoneNumberMatcher(line, None):  # None = global detection
            num_obj = match.number
            if phonenumbers.is_valid_number(num_obj):
                # Format in E.164 (machine‑friendly)
                formatted_e164 = phonenumbers.format_number(
                    num_obj, phonenumbers.PhoneNumberFormat.E164
                )
                # Format in INTERNATIONAL (human‑friendly)
                formatted_intl = phonenumbers.format_number(
                    num_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                extracted_numbers.append(f"{formatted_e164} | {formatted_intl}")

    # Deduplicate
    extracted_numbers = list(set(extracted_numbers))

    # Save extracted numbers
    output_path = os.path.join("downloads", f"extracted_{document.file_name}.txt")
    with open(output_path, "w", encoding="utf-8") as out:
        for num in extracted_numbers:
            out.write(num + "\n")

    # Send file back with summary
    await update.message.reply_document(
        document=InputFile(output_path),
        caption=(
            f"✅ Extraction complete!\n"
            f"Total Lines: {total_lines}\n"
            f"Total Extracted: {len(extracted_numbers)}"
        )
    )

# --- Main ---
def main():
    # Replace with your bot token
    app = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
