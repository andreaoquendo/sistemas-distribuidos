import { createGlobalStyle } from "styled-components";

const GlobalStyle = createGlobalStyle`
    *, *::before, *::after {
        box-sizing: border-box;
    }

    html, body {
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        background: #f8f9fa;
        color: #222;
        min-height: 100vh;
    }

    a {
        color: inherit;
        text-decoration: none;
    }

    ul, ol {
        padding: 0;
        margin: 0;
        list-style: none;
    }

    button {
        font-family: inherit;
        cursor: pointer;
        border: none;
        background: none;
    }

    h1, h2, h3, h4, h5, h6 {
        margin: 0;
        padding: 0;
    }
`;

export default GlobalStyle;
