import google.generativeai as genai


GOOGLE_API_KEY = "AIzaSyBmu4sInyBV3jSHSGRA2bdjW_kDf1wsZ_A"


def main():

    genai.configure(
        api_key=GOOGLE_API_KEY
    )

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    response = model.generate_content(
        """
        Xin chào.

        Hãy trả lời bằng tiếng Việt.

        Hãy giới thiệu bản thân trong 3 câu.
        """
    )

    print(
        "\n===== RESPONSE =====\n"
    )

    print(
        response.text
    )


if __name__ == "__main__":

    main()