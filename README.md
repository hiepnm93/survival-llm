# Survival LLM

> **Ghi chú về bản fork.** Đây là bản fork của [anonnerdfrenzy/survival-llm](https://github.com/anonnerdfrenzy/survival-llm)
> do Ronny Fernandez thực hiện (giấy phép MIT, xem `LICENSE`; nội dung thư viện giữ giấy phép riêng của nó, xem `SOURCES.md`).
> Mọi công lao về ứng dụng, thư viện và các bài eval đều thuộc về dự án gốc.
>
> *English version: [README.en.md](README.en.md).*
>
> Bản fork này thay đổi những gì: nó thêm **Qwen3.6 35B-A3B** (bản GGUF của unsloth `UD-Q4_K_XL`, 22.4 GB,
> `hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL`) và đề xuất nó đầu tiên trên các máy PC có 32 GB bộ nhớ,
> nhờ vậy một máy PC với **card đồ họa 12 GB** vẫn có được một mô hình thông minh: đây là mô hình mixture-of-experts
> chỉ có 3B tham số hoạt động, nên Ollama đặt khoảng 10.8 GB lên GPU và phần còn lại trong bộ nhớ hệ thống.
> Đã thử với Ollama 0.30.10 trên RTX 3080 Ti 12 GB + 64 GB RAM (Linux): gọi tool hoạt động, khoảng
> 46 token mỗi giây, tổng cộng khoảng 32 GB ở mức ngữ cảnh 32k của ứng dụng. Nó **chưa** trải qua các bài
> eval an toàn được chấm mù của dự án gốc ở bên dưới, nên hãy kiểm tra nguồn của nó như với mọi mô hình khác.
> Qwen3.6 nhận các mức suy luận `low`/`medium`/`high`/`max` (không có `xhigh`), nên `core.py` cho nó một họ riêng.
> Bản fork này không phát hành bản build nào; hãy chạy nó từ mã nguồn. Phần kiểm tra cập nhật của ứng dụng vẫn trỏ về dự án gốc.
>
> Đã có sẵn file GGUF? `printf 'FROM /path/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf\n' > Modelfile &&
> ollama create qwen3.6-35b-a3b -f Modelfile` (bất kỳ tên nào có chứa `qwen3.6` đều chọn đúng cấu hình).

Một trợ lý AI miễn phí kèm thư viện sinh tồn, chạy hoàn toàn trên máy tính của bạn và hoạt động không cần
internet. Hãy hỏi nó cách giữ thực phẩm an toàn khi mất điện, cách xử lý vết bỏng hay cách làm sạch nước: nó
tìm trong một thư viện offline gồm các bài viết y khoa, cứu hộ khẩn cấp, hướng dẫn thực hành và bách khoa toàn thư,
trả lời dựa trên những gì tìm được, và chỉ cho bạn đúng đoạn văn mà mỗi câu trả lời xuất phát từ đó.

- **Offline và riêng tư.** Mô hình AI và thư viện nằm trên máy tính của bạn. Câu hỏi của bạn không bao giờ rời khỏi máy, và sau khi cài đặt xong thì nó hoạt động với internet đã tắt.
- **Chỉ rõ nguồn.** Mỗi câu trả lời liệt kê những bài viết nó đã đọc; nhấp vào một bài để tự đọc, với đoạn được trích dẫn đã bôi sáng, kèm giấy phép của nó. Hãy hỏi "bạn lấy thông tin đó từ đâu?" và nó sẽ mở nguồn ra.
- **Chỉ rõ lập luận.** Nút hiện lập luận, bên dưới mỗi câu trả lời, mở ra những gì AI đã suy nghĩ trước khi trả lời, từng bước một, cùng với các lượt tìm kiếm và những bài viết nó đã đọc ở giữa. Phần này vẫn ẩn cho đến khi bạn nhấp vào. Nó suy luận nhiều hay ít là do bạn quyết định: nút Lập luận, cạnh nút Gửi, là một hạn mức (Tắt, 1.000, 4.000 hay 16.000 token, hoặc không giới hạn), và khi đến hạn mức thì nó dừng suy nghĩ và trả lời bằng những gì đang có.
- **Bạn có thể tùy chỉnh.** Nút Hướng dẫn hiển thị những chỉ dẫn mà AI nhận được trước khi bạn hỏi bất cứ điều gì (ứng dụng thêm ngày hôm nay, tên các file của bạn và các ghi chú trong Bộ nhớ của bạn vào sau đó); hãy sửa chúng rồi Lưu để thay đổi cách nó trả lời (Đặt lại sẽ mang bản gốc trở lại). Hạn mức độ dài cạnh nút Gửi đặt ra độ dài tối đa của một câu trả lời, hoặc tắt hạn mức đó đi.
- **Thêm file của riêng bạn.** Nút File của bạn, ở phía trên, nhận file PDF, tài liệu Word, ebook EPUB, trang web và file văn bản (thả chúng vào cửa sổ hoặc chọn chúng), nhờ vậy AI có thể tìm trong sách hướng dẫn máy phát điện của bạn, danh sách thuốc của bạn hay kế hoạch khẩn cấp của gia đình bạn cùng với thư viện. Chúng vẫn nằm trên máy tính của bạn, trong thư mục `Survival LLM Files` ở thư mục home của bạn; những file bạn đặt vào thư mục đó, hoặc sửa ở đó, sẽ tự được nhận. Nó chưa đọc được bản scan hay ảnh chụp trang giấy.
- **Nhớ về bạn.** Hãy nói với nó rằng con gái bạn bị dị ứng penicillin hay rằng bạn có một máy phát điện Honda, và nó lưu lại một ghi chú ngắn để các cuộc trò chuyện sau cũng biết điều đó; mỗi câu trả lời cho thấy nó đã lưu gì, kèm nút Hoàn tác. Nút Bộ nhớ, ở phía trên, hiển thị mọi ghi chú trong một danh sách bạn có thể sửa, và một công tắc tắt việc AI tự lưu (nó vẫn đọc những ghi chú bạn giữ lại). Các ghi chú vẫn nằm trên máy tính của bạn, trong một file văn bản thuần duy nhất cùng với cài đặt của ứng dụng.
- **Tự cập nhật.** Nút Kiểm tra cập nhật, ở dưới cùng cửa sổ, tìm phiên bản mới (nó cũng tự tìm mỗi ngày một lần khi đang chạy, bằng cách tải về một file nhỏ từ trang web của dự án; không có thông tin nào về bạn được gửi đi). Cập nhật ngay sẽ tải về, kiểm tra, rồi khởi động lại vào bản mới, giữ nguyên các mô hình, thư viện, file và cài đặt của bạn. Các thư viện mới hơn cũng được đề xuất ở đó.
- **Dành cho tình huống khẩn cấp.** Khoảng 1,5 triệu bài viết (500.000 bài trong bản tải về nhỏ hơn): khoảng 930.000 bài được đọc nhiều nhất của Wikipedia, WikiMed, MedlinePlus, một cẩm nang thuốc của Anh, WikEM, Ready.gov, CDC, các cẩm nang sinh tồn và sơ cấp cứu của quân đội Mỹ và FEMA, cẩm nang đóng hộp của USDA, các tài liệu tham khảo về rủi ro để ước lượng micromort (bảng sinh mệnh, tỉ lệ tử vong ở Mỹ), wikiHow, iFixit, Appropedia, Energypedia và các mục hỏi đáp thực tiễn. Xem [SOURCES.md](SOURCES.md).

## Cài đặt

Hãy làm việc này khi bạn còn internet. Sau đó thì nó không cần internet nữa. Quá trình cài đặt mất từ 20 phút đến khoảng 2 tiếng rưỡi, tùy vào
máy tính và tốc độ internet của bạn (mô hình AI lớn nhất nặng 80 GB); bạn chỉ phải bấm chuột khoảng 5 phút.

**Mac** (Apple Silicon, macOS 14 Sonoma hoặc mới hơn)
1. Tải `Survival-LLM-mac.zip` rồi nhấp đôi vào nó để giải nén. Bạn có thể chuyển **Survival LLM** vào Applications nếu muốn.
2. Nhấp đôi vào **Survival LLM**. Lần đầu tiên, macOS sẽ nói rằng nó không xác minh được ứng dụng, vì ứng dụng không được
   bán qua Apple. Hãy nhấp **Done**, mở **System Settings > Privacy & Security**, cuộn xuống dòng "Survival LLM was blocked",
   nhấp **Open Anyway**, rồi xác nhận bằng mật khẩu của bạn. Bạn chỉ phải làm việc này một lần.

**Windows** (10 hoặc 11, 64-bit)
1. Tải `Survival-LLM-windows.zip`, nhấp chuột phải vào nó và chọn **Extract All**. (Chạy trực tiếp từ bên trong file zip sẽ không được.)
2. Mở thư mục **Survival LLM** đã giải nén và nhấp đôi vào **Survival LLM.bat**. Nếu Windows nói rằng nó đã bảo vệ
   máy của bạn, hãy nhấp **More info**, rồi **Run anyway**.

**Sau đó** ứng dụng mở ra trong cửa sổ riêng và hướng dẫn bạn qua các bước cài đặt:
1. **Bộ máy AI:** đã có sẵn trong ứng dụng Mac. Trên Windows, một lần nhấp là tải được nó về (Ollama, 1.6 GB).
2. **Mô hình AI:** nó đề xuất mô hình tốt nhất cho bộ nhớ của máy bạn (bên dưới) và tải mô hình đó về.
3. **Thư viện:** "Everything" (tải về 8.8 GB) hoặc "Essentials" (1.3 GB, không có Wikipedia và iFixit).

**Dung lượng đĩa trống cần có:** kích thước của mô hình cộng 5 GB, cộng khoảng 27 GB trong lúc cài thư viện đầy đủ
(21 GB sau khi cài xong), hoặc khoảng 10 GB cho bản Essentials (3 GB sau khi cài xong).

## Gỡ cài đặt

Hãy xóa ứng dụng, rồi xóa các thư mục sau: các mô hình AI, ở `~/.ollama/models` (dùng chung với bất kỳ Ollama nào khác trên
máy, nên hãy giữ lại nếu bạn dùng Ollama cho việc khác), và thư viện, ở `~/Survival LLM Library`. Các file của riêng bạn nằm ở
`~/Survival LLM Files`; hãy giữ thư mục đó nếu bạn còn muốn chúng. Cài đặt của riêng ứng dụng
nằm ở `~/Library/Application Support/Survival LLM` trên Mac, và ở `%APPDATA%\Survival LLM` cộng với
bộ máy AI ở `%LOCALAPPDATA%\Survival LLM` trên Windows.

## Máy tính của bạn được mô hình nào

Ứng dụng kiểm tra bộ nhớ của bạn và đề xuất một mô hình. Càng nhiều bộ nhớ, mô hình càng thông minh.

| Máy tính của bạn | Mô hình | Dung lượng tải |
|---|---|---|
| Mac có 128 GB hoặc hơn | NVIDIA Nemotron 3.5 Super (`nemotron-3.5-super:120b-a12b-nvfp4`) | 80 GB |
| Mac hoặc PC có 32 GB hoặc hơn (PC: lý tưởng là card đồ họa 12 GB) | Qwen3.6 35B-A3B (`hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL`, bản fork này) | 23 GB |
| Mac có 32-96 GB | Qwen3.8 27B (`qwen3.8:27b-mlx`) | 18 GB |
| PC Windows có 32 GB hoặc hơn | NVIDIA Nemotron 3.5 Lightning (`nemotron-3.5-lightning:30b-a3b`) | 25 GB |
| Mac hoặc PC có 16-31 GB | IBM Granite 4.2 8B (`granite4.2:8b`) | 6 GB |

Nemotron Super cần 128 GB vì macOS chỉ cho phía đồ họa dùng khoảng ba phần tư bộ nhớ.

Gemma 4 E4B (`gemma4`, 10 GB) được đề xuất như một lựa chọn nhanh hơn cho các máy 16 GB. Những máy có 8 GB vẫn
có thể tìm trong thư viện; không có mô hình nào chúng tôi thử vừa đủ nhỏ lại vừa đủ an toàn để đề xuất cho chúng.

## Các mô hình làm được đến đâu

Mỗi mô hình trả lời 22 câu hỏi về mất điện và sơ cấp cứu (thực phẩm, máy phát điện, nước, khí carbon monoxide,
hạ nhiệt độ cơ thể, chảy máu, bỏng, insulin, đường dây điện bị đứt rơi, bụi phóng xạ, ngộ độc botulinum và nhiều nữa) bằng
toàn bộ ứng dụng: prompt, các tool và chức năng tìm kiếm thư viện của nó. Sau đó các giám khảo AI độc lập chấm mù mọi câu trả lời
(tên mô hình được che, thứ tự được đảo) dựa trên hướng dẫn chính thức của USDA, CDC, FEMA, EPA, NHS, WHO và Hội Chữ thập đỏ: một giám khảo
cho độ chính xác, một cho độ an toàn, và một người phản biện kiểm tra lại mọi câu trả lời bị đánh dấu là có hại.

Nói thẳng về cách đo các con số này: các bài kiểm tra chạy trên một bản build cũ hơn của thư viện, trước khi Wikipedia
được thêm vào, bản đó cũng chứa một số tài liệu không có trong các bản tải về công khai (các bộ sưu tập "zimgit" của Kiwix và
các trang bách khoa toàn thư cùng trang thuốc có bản quyền của MedlinePlus; mỗi mô hình có từ 1 đến 10 câu trả lời đã đọc một trong số đó). Phần
hướng dẫn của ứng dụng từ đó cũng có thêm các quy tắc mới: quy tắc về khí carbon monoxide và "luôn đưa ra ước lượng tốt nhất của bạn". Hãy xem
bảng này như một phép so sánh giữa các mô hình, không phải một lời bảo đảm cho phiên bản bạn tải về.

| Mô hình | Độ chính xác | Đúng ý chính | Câu trả lời có hại | Số giây mỗi câu trả lời* |
|---|---|---|---|---|
| Nemotron 3.5 Super | 86% | 21 trên 22 | 0 | 12 |
| Qwen3.8 27B | 80% | 21 trên 22 | 0 | 40 |
| Nemotron 3.5 Lightning | 77% | 19 trên 22 | 1 | 8 |
| Qwen 3.6 (36B MoE) | 59% | 15 trên 22 | 1 | 24 |
| Granite 4.2 8B | 55% | 14 trên 22 | 0 | 29 |
| Granite 4.2 30B | 55% | 11 trên 22 | 2 | 55 |
| Gemma 4 E4B | 48% | 11 trên 22 | 0 | 3 |
| Granite 4.2 3B | 44% | 8 trên 22 | 5 (2 câu có thể gây chết người) | 12 |

\* Trên một MacBook Pro M4 Max (128 GB), Ollama 0.40.9. Qwen3.8 27B được thử ở bản build 4-bit của mlx-community
(`local-ai2` trong `evals/results`); ứng dụng tải về bản build NVFP4 của Ollama cho cùng mô hình đó. Nemotron Super xuất hiện
ở đó dưới tên `local-ai1` (cùng mô hình đó với cấu hình của ứng dụng). Windows tải về một file khác của Nemotron
Lightning (Q4_K_M) so với bản Mac được thử ở đây. Độ chính xác là tỉ lệ điểm đạt được trên thang 0-3 cho mỗi câu trả lời; "có hại"
nghĩa là làm theo nó có thể gây tổn thương cho người khác. Granite 4.2 3B, ban đầu dự định cho các máy 8 GB, không được đề xuất: nó
bảo người ta không dùng dây garô cho cánh tay và chỉ đứng cách đường dây điện bị đứt rơi 3 feet (hướng dẫn là 35).
Qwen 3.6 cũng không được đề xuất: nó bị mắc vào vòng lặp tự nhắc lại ở hai câu hỏi (một lần kéo dài 94 phút),
đó cũng là lý do các câu trả lời có hạn mức độ dài (bạn có thể đổi nó, hoặc tắt nó, ở cạnh nút Gửi).

Các bài kiểm tra đã tìm ra và sửa được hai vấn đề cho mọi mô hình: một số mô hình cứ tra cứu mãi cho đến khi hết lượt
tra cứu mà không bao giờ trả lời (giờ chúng được yêu cầu trả lời bằng những gì đã đọc), và vài mô hình đưa ra các ngoại lệ kiểu "nếu
bắt buộc phải làm" cho việc chạy xe hơi và máy phát điện gần nhà (prompt giờ đã loại bỏ hẳn những trường hợp đó).
Để chạy lại, dùng `evals/retrieval_eval.py`, `evals/make_judging_batches.py` và `evals/score_judging.py`;
các câu trả lời nằm ở `evals/results/`, điểm chấm nằm ở `evals/judging/`.

**Nguồn bị bịa ra.** Mỗi câu trả lời kết thúc bằng dòng "Sources:" của chính mô hình, và phần hướng dẫn của nó nói rằng ứng dụng hiển thị
mọi bài viết mà nó đã mở. Dù vậy các mô hình vẫn nêu tên những nguồn chúng chưa từng xem. Trong một bài kiểm tra riêng gồm 14 câu hỏi
(`evals/citation_check.py`, ngày 24 tháng 10 năm 2026), số câu trả lời nêu tên một nguồn mà mô hình vừa không mở lại vừa không thấy trong
kết quả tìm kiếm của nó là: Nemotron Super 6 câu (phần lớn là trả lời từ ký ức rồi nêu tên Ready.gov hay CDC), Lightning 3 câu,
Gemma 3 câu, Granite 2 câu và Qwen3.8 27B 1 câu. Nên ứng dụng kiểm tra dòng đó so với những gì mô hình đã mở hoặc đã thấy, và thay
một dòng nêu tên bất cứ thứ gì khác bằng danh sách những bài viết nó thực sự đã đọc.

### Kết quả đo của bản fork

Đây là **điểm fact-check tự động** (script eval `evals/retrieval_eval.py`, 22 câu), **chưa** phải điểm chấm mù
về độ an toàn như bảng ở trên — nên đừng đọc nó như một lời bảo đảm về độ an toàn. Mô hình là Qwen3.6-35B-A3B
`UD-Q4_K_XL` qua Ollama trên RTX 3080 Ti 12 GB + 64 GB RAM, chạy với hai thư viện: **lite** và **đầy đủ** (8.8 GB).

| Chỉ số | Qwen3.6-35B-A3B UD-Q4_K_XL, thư viện lite | Qwen3.6-35B-A3B UD-Q4_K_XL, thư viện đầy đủ | Qwen 3.6 của dự án gốc |
|---|---|---|---|
| Điểm fact | 0.902 | **0.955** | 0.856 |
| Có đủ mọi ý chính | 17/22 | **19/22** | 16/22 |
| Đã tìm kiếm | 22/22 | 22/22 | 22/22 |
| Đã đọc bài | 15/22 | 19/22 | 14/22 |
| Có liên quan | 16/22 | 19/22 | 19/22 |
| Có trích dẫn | 20/22 | 22/22 | 18/22 |
| Giây mỗi câu (trung bình) | 30.2 | 33.7 | 275.1 (có vòng lặp) |
| Câu chậm nhất | 65 s | 61 s | — |

Tốc độ sinh 46.2 token/giây ở cả hai lần. Không lần nào bị lặp: không câu nào mắc vào vòng lặp tự nhắc lại
như Qwen 3.6 ở bảng trên. Thư viện đầy đủ giúp mô hình đọc được bài liên quan nhiều hơn, nên điểm fact tăng;
ba câu còn thiếu ý là: chế độ tiết kiệm pin, khử trùng nhà vệ sinh tạm, và vứt bỏ đồ ăn hỏng.

Kết quả thô ở `evals/results/qwen36-a3b-lite/` và `evals/results/qwen36-a3b-full/`. Dòng Qwen 3.6 của dự án gốc lấy từ
`evals/results/summary.jsonl` (mô hình `qwen3.6`).

## Nó hoạt động thế nào

```
your question ─► local model (Ollama) ─► search_library ─► SQLite full-text index ─► passages
                        ▲                read_article  ─► plain-text library files
                        └──── answer with "Sources:" ◄──┘   show_article ─► opens it on screen
```

- `app/server.py` phục vụ trang chat chỉ trên `127.0.0.1` và đưa mỗi lượt trò chuyện qua `core.py`.
- `core.py` truyền phát câu trả lời của mô hình và chạy các tool thư viện của nó: `search_library`, `read_article`, `show_article`.
- `library/search.py` tìm trong `index.sqlite` (FTS5, xếp hạng BM25 trên các đoạn văn khoảng 1.500 ký tự, nguồn chính thức được xếp hạng cao hơn) và đọc các shard Markdown văn bản thuần.
- `memory.py` giữ các ghi chú của AI về người dùng (`survival-llm-memory.txt`, nằm cùng cài đặt của ứng dụng) và, trong khi người dùng còn cho phép, `core.py` cho mô hình thêm một lượt ngắn sau các câu trả lời cho những tin nhắn nói về người dùng hoặc gia đình họ, để nói xem cần nhớ, sửa hay quên điều gì (một phản hồi JSON mà ứng dụng kiểm tra rồi áp dụng). Các ghi chú, ngày hôm nay và tên các file của người dùng được thêm vào sau phần hướng dẫn khi một cuộc trò chuyện bắt đầu.
- `library/myfiles.py` đọc các file của riêng người dùng vào một chỉ mục riêng nhỏ (giữ cùng cài đặt của ứng dụng) và tìm trong đó cùng với thư viện.
- Mọi thứ, trừ Ollama, cửa sổ ứng dụng (pywebview), phần đọc PDF (pypdf) và phần kiểm tra chứng chỉ web bằng kho chứng chỉ của hệ thống (truststore), đều là thư viện chuẩn của Python.

## Chạy từ mã nguồn

```bash
python3 app/server.py          # the app in its own window (needs `pip install pywebview pypdf truststore`; else it uses your browser)
python3 app/server.py --browser                     # in your web browser instead
python3 chat.py "How long is fridge food safe in a blackout?"   # terminal; --model NAME picks a model
```

Thư viện được tìm ở `$SURVIVAL_LLM_LIBRARY`, rồi `~/Survival LLM Library`, rồi `library.noindex/` nằm cạnh mã nguồn.
Khi không có bộ máy sẵn bên trong, ứng dụng dùng bản Ollama bạn đã cài (`ollama serve`).

`python3 tests/run_all.py` kiểm tra bộ nhớ và việc xử lý những gì mô hình viết ra (yêu cầu quên, ghi chú về những
người khác nhau, các dòng Sources), với một bản giả lập thay cho mô hình: không cần Ollama hay thư viện. Hãy chạy nó sau khi sửa `memory.py` hoặc
`core.py`, và chạy `evals/memory_eval.py --step MODEL ...` để xem các mô hình thật làm được đến đâu.

## Thử các thay đổi dưới dạng ứng dụng Mac

```bash
bin/dev              # "Survival LLM Dev": the Mac app running the code in this folder (restarts it if it's open)
bin/dev --fresh      # the same, as a brand-new person sees it: no library, memory, files or settings
bin/dev --release    # build the Mac app exactly as it ships (packaging/build.sh mac) and run that build
bin/dev stop         # quit it; bin/dev reset deletes its settings, memory and files; bin/dev log follows its log
```

Survival LLM Dev được build một lần vào `~/Applications` (`--rebuild` build lại nó) với cùng Python, pywebview và
Ollama như ứng dụng thật, nhưng mã nguồn của nó là một liên kết tới thư mục này, nên mỗi lần khởi động đều chạy mã nguồn ở trạng thái lúc đó; Spotlight
cũng mở được nó. Nó giữ cài đặt, bộ nhớ và file riêng của mình trong `~/Library/Application Support/Survival LLM Dev`, nên một bản
Survival LLM đã cài sẽ không bị ảnh hưởng, và nó dùng chung thư viện cùng các mô hình AI. Một nhãn Dev và dòng chữ ở
dưới cùng cửa sổ cho biết nó đang chạy nhánh và commit nào, và nó không bao giờ tự cập nhật. Log của nó là
`~/Library/Logs/Survival LLM Dev.log`.

## Build thư viện

```bash
python3 -m venv .venv && .venv/bin/pip install libzim lxml trafilatura
python3 library/fetch_zims.py        # Kiwix ZIM sources (about 50 GB, temporary)
python3 library/fetch_manuals.py     # U.S. government, IFRC and WHO manuals
.venv/bin/python library/fetch_risk.py   # risk references (death-rate statistics, micromort articles)
curl -L -o library.noindex/raw/wikihowAll.csv \
  https://huggingface.co/datasets/Lajvi/wikihowAll/resolve/main/wikihowAll.csv   # wikiHow (620 MB)
.venv/bin/python library/build_library.py      # plain text + index in library.noindex/
```

`build_library.py` build theo kiểu tăng dần (các nguồn đã xong sẽ được bỏ qua) và `--rebuild KEY ...` làm lại các nguồn.
Nó cần `pdftotext` (poppler) cho các cẩm nang PDF.

**Một bản build mặc định chỉ dành cho việc dùng riêng của bạn:** nó chứa tài liệu có thể không được phép chia sẻ (xem SOURCES.md).
Để build các bản tải về có thể chia sẻ được:

```bash
LIBRARY_OUT=dist/library-full .venv/bin/python library/build_library.py --public
LIBRARY_OUT=dist/library-lite .venv/bin/python library/build_library.py --lite
python3 packaging/make_packs.py --base-url https://github.com/OWNER/survival-llm/releases/download/vX.Y.Z \
  lite=dist/library-lite full=dist/library-full   # parts for the release + library-packs.json for docs/
```

Các pack có kèm ngày (`--version`, mặc định là hôm nay); các bản đã cài sẽ đề xuất một pack có ngày mới hơn như một bản cập nhật.

## Đóng gói ứng dụng

```bash
packaging/build.sh     # dist/Survival-LLM-mac.zip and dist/Survival-LLM-windows.zip (needs Xcode's command-line tools)
gh release create "v$(cat packaging/VERSION)" dist/Survival-LLM-mac.zip dist/Survival-LLM-windows.zip
python3 packaging/make_update.py "What's new" "..."   # writes docs/update.json; publish docs/ afterwards
```

Hãy đặt số phiên bản trong `packaging/VERSION` trước. Các bản đã cài đọc `docs/update.json` từ trang web của dự án,
tải về file zip cho hệ thống của mình, kiểm tra kích thước và SHA-256 của nó, rồi tự thay thế chính mình bằng bản đó.

Ứng dụng Mac đóng gói kèm một bản Python di động, pywebview cho cửa sổ của nó, và Ollama. Ứng dụng Windows đóng gói kèm Python và
pywebview rồi tải Ollama về khi dùng lần đầu (nó nặng 1.6 GB kèm theo các thư viện card đồ họa).

## Giấy phép

Mã nguồn: MIT ([LICENSE](LICENSE)). Nội dung thư viện giữ giấy phép của nguồn gốc ([SOURCES.md](SOURCES.md)).

Các mô hình AI vẫn mắc lỗi. Mỗi câu trả lời đều hiển thị nguồn của nó để bạn có thể kiểm tra.
