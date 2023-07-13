_font_title = "Monoton"
_font_subtitle = "Exo"

CSS = (
    """
<!-- Add the font link from Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family="""
    + _font_title
    + """&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family="""
    + _font_subtitle
    + """&display=swap" rel="stylesheet">

<style>
    /* Remove the streamlit header */
    header[data-testid="stHeader"]  {
        display: none;
    }
    /* Remove the sidebar menu */
    div[data-testid="collapsedControl"]{
        display: none;
    }
    /* Background */
    .css-z5fcl4 {
        padding: 0.5rem;
        padding-top: 0rem;
    }

    /* Distances between the title and the image in mobile */
    .css-1uifejx.e1tzin5v1 {
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    h1 {
        padding-top: 0px;
    }


    /* Center the image within its container */
    .css-1kyxreq {
    justify-content: center;
    }

    /* Remove fixed width from the image container */
    .css-1kyxreq.etr89bj2 {
    width: 100% !important;
    }

    /* Center the title */
    .css-k7vsyb {
    text-align: center;
    }

    /* Hide the anchor button */
    .css-zt5igj.e16nr0p33 a {
        display: none;
    }
    /* Hide the full screen button */
    .css-e370rw.e19lei0e1 {
        display: none;
    }
    .css-6awftf.e19lei0e1 {
        display: none;
    }

    /* Desktop */
    @media (min-width: 640px) {
        .stMarkdown {
            max-width: 100%;
            width: auto;
            display: inline-block;
        }
        /* Dynamically add space between the image and the title */
        .css-1kyxreq {
            justify-content: right;
        }
    }

    /* Add space after the image and the title */
    .css-1a32fsj {
        margin-right: 0px;
    }

    /* Apply the futuristic font to the text title*/
    #moseca {
        font-family: '"""
    + _font_title
    + """', sans-serif;
        font-size: 3rem;
        text-align: center;
        /* Align the text to the center of the box */
        align-items: center;
        /* Set the line height to the same as the height of the box */
        line-height: 3.5rem;
        margin-bottom: -1rem;
    }

    /* subtitle */
    .css-5rimss p, .css-nahz7x p {
        font-family: """
    + _font_subtitle
    + """, sans-serif;
        font-size: 0.8rem;
        text-align: center;
    }

    #extract-vocals-instrumental-from-any-song, #play-karaoke-removing-the-vocals-of-your-favorite-song {
        font-family: """
    + _font_subtitle
    + """, sans-serif;
    }

    /* Desktop */
    @media (min-width: 640px) {
        .css-zt5igj, .css-nahz7x p {
            text-align: left;
        }
        .css-5rimss p {
            text-align: left;
        }
    }

    .st-af {
        align-items: center;
        padding-right: 2rem;
    }

    /* Remove the gap around the player */
    .css-434r0z {
        gap: 0rem;
    }

    /* center the audio player in Separate page */
    .css-keje6w.e1tzin5v1 {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>

"""
)


CSS_TABS = """<style>
        div[data-baseweb="tab-list"] {
            display: flex !important;
            align-items: center !important;
            justify-content: space-evenly !important;
            flex-wrap: wrap !important;
                .css-q8sbsg.e16nr0p34 p{
                    font-size: 1.1rem !important;
                }
        }
        </style>"""
