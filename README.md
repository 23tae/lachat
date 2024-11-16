# LaChat

![thumbnail](/assets/thumbnail.png)

LaChat은 RAG 기반 AI 챗봇 애플리케이션입니다. 사용자가 업로드한 문서를 분석하여 관련 질문에 답변합니다.

## 주요 기능

- 다양한 형식의 문서 업로드 지원 (PDF, DOCX, PPTX)
- 문서 내용 기반 질의응답
- 대화 기록 유지

## 사용 기술

* [![LangChain]][LangChain url]
* [![OpenAI]][OpenAI url]
* [![Hugging Face]][Hugging Face url]
* [![Streamlit]][Streamlit url]

## 설치 방법

1. 가상 환경을 생성하고 활성화합니다:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

2. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

3. `.env` 파일을 생성하고 OpenAI API 키를 추가합니다:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 사용 방법

1. 애플리케이션을 실행합니다:
   ```
   streamlit run src/main.py
   ```

2. 사이드바에서 문서를 업로드하고 "Start Processing" 버튼을 클릭합니다.

3. 문서 처리가 완료되면, 채팅 인터페이스에서 질문을 입력합니다.

4. AI assistant의 답변을 확인합니다.

5. 필요한 경우 답변을 클립보드에 복사합니다.
  ![copy](/assets/copy_to_clipboard.png)

## 주의사항

- 이 애플리케이션은 OpenAI API를 사용하므로, API 사용에 따른 비용이 발생할 수 있습니다.
- 대용량 문서를 처리할 때는 시간이 걸릴 수 있습니다.

<!-- MARKDOWN LINKS & IMAGES -->
[LangChain]: https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white
[LangChain url]: https://python.langchain.com/
[OpenAI]: https://img.shields.io/badge/openai-412991?style=for-the-badge&logo=openai&logoColor=white
[OpenAi url]: https://openai.com/
[Hugging Face]: https://img.shields.io/badge/huggingface-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black
[Hugging Face url]: https://huggingface.co/
[Streamlit]: https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white
[Streamlit url]: https://streamlit.io/
