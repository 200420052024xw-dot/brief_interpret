from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="15e0122b-bf1e-415f-873b-1cb6b39bb612"
)

def llm(content,prompt,model="doubao-seed-1-6-flash-250828"):

    messages=[
        {"role":"system","content":prompt},
        {"role":"user","content": content},]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content