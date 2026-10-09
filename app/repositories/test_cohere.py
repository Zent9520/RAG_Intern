import cohere


COHERE_API_KEY = "cohere_1iicOF3a7HVVo7dO9QYAVftDL2C34qxxhpvTrgy60C1oov"


def main():

    client = cohere.ClientV2(
        api_key=COHERE_API_KEY
    )

    response = client.chat(

        model="command-a",

        messages=[
            {
                "role": "user",
                "content":
                "Xin chào. Hãy giới thiệu bản thân bằng tiếng Việt."
            }
        ]
    )

    print(
        "\n===== RESPONSE =====\n"
    )

    print(
        response.message.content[0].text
    )


if __name__ == "__main__":

    main()