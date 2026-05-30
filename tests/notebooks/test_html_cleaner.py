# tests/notebooks/test_html_cleaner.py

from notebooks.html_cleaner import clean_html


class TestHtmlCleaner:

    def test_removes_403_title_and_h1(self):
        raw = """
<!DOCTYPE html>
<head><title>403 Forbidden</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <style type=\"text/css\">  body {
        background: white;
    }

    main {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        min-width: 95vw;
    }

    main h1 {
        font-weight: 400;
        font-size: 4.6em;
        color: #191919;
        margin: 0 0 11px 0;
    }

    main p {
        font-size: 1.4em;
        color: #3a3a3a;
        font-weight: 400;
        line-height: 2em;
        margin: 0;
    }

    main p a {
        color: #3a3a3a;
        text-decoration: none;
        border-bottom: solid 1px #3a3a3a;
    }

    body {
        font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif;
        font-size: 12px;
    }

    footer {
        position: absolute;
        bottom: 22px;
        left: 0;
        width: 100%;
        text-align: center;
        line-height: 2em;
    }

    footer span {
        margin: 0 11px;
        font-size: 1em;
        font-weight: 400;
        color: #a9a9a9;
        white-space: nowrap;
    }

    footer span strong {
        font-weight: 400;
        color: #191919;
    }

    @media (max-width: 600px) {
        body {
            font-family: \"Helvetica Neue\", Helvetica, Arial, Sans-Serif;
        }
    }  </style>
</head>
<body>
<main><h1>403 Forbidden</h1></main>
<footer><span><strong>8cWEusDw/71kMe7qo @ Fri, 29 May 2026 14:07:44 UTC</strong></span> <span></span></footer>
</body></html>
        """

        cleaned = clean_html(raw)

        # Title must be neutralized
        assert "<title></title>" in cleaned

        # H1 must also be neutralized
        assert "<h1>" in cleaned
        assert "403" not in cleaned.lower()
        assert "forbidden" not in cleaned.lower()

        # Meta must remain
        assert 'meta name="viewport"' in cleaned

        # Body content must be removed
        assert "<p>" not in cleaned
        assert "Some body text" not in cleaned

    def test_keeps_normal_title_and_h1(self):
        raw = """
        <html>
          <head>
            <title>My Business</title>
            <meta name="description" content="Great services">
          </head>
          <body>
            <h1>Welcome</h1>
          </body>
        </html>
        """

        cleaned = clean_html(raw)

        assert "<title>My Business</title>" in cleaned
        assert "<h1>Welcome</h1>" in cleaned
        assert "Great services" in cleaned
        assert "<p>" not in cleaned

    def test_handles_empty_html(self):
        cleaned = clean_html("")
        assert "<title>" in cleaned
        assert "<h1>" in cleaned
