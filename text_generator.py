from faker import Faker

def generate_typing_text(mode_type, intensity):
    """
    Generates a block of text using Faker based on user settings.
    mode_type: 'time' (minute-based) or 'page' (length-based)
    intensity: 1, 2, or 3 (representing minutes or pages)
    """

    fake = Faker()

    # Calculate target word count to ensure they never run out
    if mode_type == 'time':
        # Target ~250 words per minute selected
        word_count = intensity * 250
    else:
        # Target ~300 words per page selected
        word_count = intensity * 300

    generated_text = ""
    while len(generated_text.split()) < word_count:
        generated_text += fake.paragraph(nb_sentences=5) + " "

    return generated_text.strip()
