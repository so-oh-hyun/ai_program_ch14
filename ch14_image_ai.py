import streamlit as st
from openai import OpenAI
import base64
import pandas as pd
import re

# 이미지 인코딩 함수 정의
def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

# 이미지 분석 함수 정의
def analyze_image(base64_image, prompt, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64, {base64_image}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content

# 마크다운-데이터프레임 변환 함수 정의
def markdown_to_dataframes(markdown_text):
    # 마크다운 표를 찾기 위한 정규 표현식 패턴
    table_pattern = r"\|(.+)\|\n\|(-+\|)+\n(((\|.+\|\n)+\|.+\|)\n?)"
    tables = re.findall(table_pattern, markdown_text)
    dataframes = []
    for table in tables:
        header = table[0].strip().split("|")
        data_rows = table[2].strip().split("\n")
        header = [h.strip() for h in header if h.strip()]
        data = [
            [cell.strip() for cell in row.split("|") if cell.strip()]
            for row in data_rows
        ]
        column_counts = {}
        new_header = []
        for col in header:
            if col in column_counts:
                column_counts[col] += 1
                new_col_name = f"{col}_{column_counts[col]}"
            else:
                column_counts[col] = 0
                new_col_name = col
            new_header.append(new_col_name)
        df = pd.DataFrame(data, columns=new_header)
        dataframes.append(df)
    return dataframes

def main():
    st.set_page_config(layout="wide")
    st.title("이미지 분석 프로그램")
    st.caption("이미지를 업로드하면 분석 결과가 출력됩니다.")
    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
        )
        st.markdown(
            "[OpenAI API Key 받기](https://platform.openai.com/account/api-keys)"
        )
    # 파일 업로드 위젯 구현
    image_file = st.file_uploader(
        "이미지를 업로드하세요.",
        type=["jpg", "jpeg", "png"],
        label_visibility="hidden",
    )
    if st.button("이미지 분석"):
        if not openai_api_key:
            st.info("계속하려면 OpenAI API Key를 추가하세요.")
            st.stop()
        if not image_file:
            st.warning("이미지를 업로드하세요.")
            st.stop()
        client = OpenAI(api_key=openai_api_key)
        with st.spinner("이미지 분석 중..."):
            # 이미지 인코딩 함수 호출
            base64_image = encode_image(image_file)
            # 프롬프트 작성
            prompt = f"""
            너는 최고의 데이터 분석가야.
            - 데이터를 분석해 핵심 내용을 정리한 표와 그에 관한 인사이트를 보여줘.
            - 표는 마크다운으로 만들어.
            - 최소한 두 가지 이상의 인사이트를 제시해.
            - 분석 결과만 응답해.
            """
            # 이미지 분석 함수 호출 및 결과 출력
            result = analyze_image(base64_image, prompt, client)
            st.write(result)
            # 마크다운-데이터프레임 변환 함수 호출 및 결과 출력
            dataframes = markdown_to_dataframes(result)
            st.write("## 데이터 다운로드")
            for df in dataframes:
                st.dataframe(df)

if __name__ == "__main__":
    main()
