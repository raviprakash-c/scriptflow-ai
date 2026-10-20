# Sources, models and licences

- Python standard library: Python Software Foundation License.
- FastAPI: MIT; Pydantic: MIT; Uvicorn: BSD-3-Clause; HTTPX: BSD-3-Clause.
- pytest (development): MIT.
- FFmpeg: inspect the exact binary build and enabled codec licences for distribution.
- edge-tts: MIT client package; review upstream voice/service terms and network dependency before commercial deployment.
- Optional faster-whisper: MIT package licence; verify selected model weights/terms.
- Pexels API: official docs at https://www.pexels.com/api/documentation/. Pexels states that its photos/videos are available for commercial use under the Pexels License, subject to its terms. API use requires a key and a prominent Pexels link; credit the contributor where possible. See https://www.pexels.com/license and https://www.pexels.com/terms-of-service.
- Pixabay API: official video endpoint docs at https://pixabay.com/api/docs/. Pixabay's Content License permits commercial and non-commercial use subject to prohibited uses; API use requires a key and displayed results should identify Pixabay as the source. See https://pixabay.com/service/license-summary/ and https://pixabay.com/service/terms/.
- The code stores stock video page URLs and contributor attribution in the timeline/manifest. This does not guarantee rights to every depicted person, logo, trademark or third-party work; review those separately.
- Local procedural SVG visuals are placeholders, not third-party stock footage, and are not certified for commercial use.
- No API key is included in the repository. Live provider behaviour has not been verified against the user's accounts.

Before production, record the actual provider, API/model identifier and version, per-asset source URL, licence, attribution, commercial-use status, retrieval time and cost. Confirm rights for each asset and every fallback path.
