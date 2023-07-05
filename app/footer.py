import streamlit as st
from htbuilder import HtmlElement, a, div, img, p, styles
from htbuilder.units import percent, px
from streamlit.components.v1 import html


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>
      footer {visibility: hidden;}
     .stApp { bottom: 50px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1,
        align_items="center",
        flex_direction="column",
        display="flex",
    )
    body = p(
        id="myFooter",
        style=styles(
            margin=px(0, 0, 0, 0),
            padding=px(5),
            font_size="0.9rem",
            color="rgb(51,51,51)",
            font_family="Exo",
        ),
    )
    foot = div(style=style_div)(body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str) or isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

    js_code = """
    <script>
    function rgbReverse(rgb){
        var r = rgb[0]*0.299;
        var g = rgb[1]*0.587;
        var b = rgb[2]*0.114;

        if ((r + g + b)/255 > 0.5){
            return "rgb(49, 51, 63)"
        }else{
            return "rgb(250, 250, 250)"
        }

    };
    var stApp_css = window.parent.document.querySelector("#root > div:nth-child(1) > div > div > div");
    window.onload = function () {
        var mutationObserver = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    var bgColor = window.getComputedStyle(stApp_css).backgroundColor.replace("rgb(", "").replace(")", "").split(", ");
                    var fontColor = rgbReverse(bgColor);
                    var pTag = window.parent.document.getElementById("myFooter");
                    pTag.style.color = fontColor;
                });
            });

            /**Element**/
            mutationObserver.observe(stApp_css, {
                attributes: true,
                characterData: true,
                childList: true,
                subtree: true,
                attributeOldValue: true,
                characterDataOldValue: true
            });
    }


    </script>
    """
    html(js_code)


def footer():
    myargs = [
        "Made in 🇮🇹 with ",
        link(
            "https://streamlit.io/",
            image("https://streamlit.io/images/brand/streamlit-mark-color.png", width="18px"),
        ),
        " by ",
        link("https://twitter.com/grsFabio", "@grsFabio"),
        "&nbsp;&nbsp;&nbsp;",
        link(
            "https://www.buymeacoffee.com/fabiogra",
            image("https://i.imgur.com/YFu6MMA.png", margin="0em", align="top", width="130px"),
        ),
    ]
    layout(*myargs)
