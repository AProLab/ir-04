import streamlit as st
import requests
import base64


class MathProblemSolver:
    """수학 문제 이미지를 분석하는 클래스"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _encode_image(self, file_image):
        """이미지 파일을 base64로 인코딩"""
        file_image.seek(0)
        image_bytes = file_image.read()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _build_prompt(self, base64_image: str):
        """API 요청 메시지 구성"""
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                            당신은 초등학교 수학 선생님입니다.
                            입력된 이미지의 수학문제에 대해, [출력 예1]과 같이 초등학생에게 설명하듯 출력해주세요.

                            [출력 예 1]

                            **[정답]**: [여기에 정답 출력]
                          
                            **[해설]**: [여기에 문제 풀이해설을 한 문장으로 출력]

                            입력된 사진으로 수학 문제를 인식할 수 없거나, 관련 없는 사진일 경우 [출력 예 2]와 같이 출력하세요
                            
                            [출력 예 2]
                            **죄송합니다. 인식할 수 없는 사진입니다.**
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]

    def analyze(self, file_image):
        """수학 문제 이미지 분석"""
        base64_image = self._encode_image(file_image)
        messages = self._build_prompt(base64_image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-5",  # GPT-5 모델 사용
            "messages": messages
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


class MathProblemApp:
    """수학 문제 풀이 Streamlit UI 클래스"""
    def __init__(self):
        self.api_key = None
        self.file_image_math = None

    def run(self):
        """Streamlit 앱 실행"""
        st.header("수학 문제 풀이")
        self.api_key = st.text_input("OPENAI API KEY를 입력하세요.", type="password")
        self.file_image_math = st.file_uploader("수학 문제 사진만 업로드하세요!", type=['png', 'jpg', 'jpeg'])

        if self.api_key and self.file_image_math:
            solver = MathProblemSolver(self.api_key)
            st.image(self.file_image_math, width=500)

            with st.spinner("수학 문제 풀이중..."):
                try:
                    result = solver.analyze(self.file_image_math)
                    st.markdown(result)
                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 오류: {e}")


if __name__ == "__main__":
    app = MathProblemApp()
    app.run()