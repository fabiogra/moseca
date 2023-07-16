import streamlit as st

from header import header
from footer import footer
from helpers import delete_old_files


def body():
    with st.columns([2, 3, 2])[1]:
        st.markdown(
            """
        <center>

        ## Welcome to Moseca, your personal web application designed to redefine your music experience.
        <font size="3"> Whether you're a musician looking to remix your favorite songs, a karaoke
        enthusiast, or a music lover wanting to dive deeper into your favorite tracks,
        Moseca is for you. </font>

        <br>

        ### High-Quality Stem Separation

        <center><img title="High-Quality Stem Separation" src="https://i.imgur.com/l7H8YWL.png" width="60%" ></img></center>


        <br>

        <font size="3"> Separate up to 6 stems including 🗣voice, 🥁drums, 🔉bass, 🎸guitar,
        🎹piano (beta), and 🎶 others. </font>

        <br>

        ### Advanced AI Algorithms

        <center><img title="Advanced AI Algorithms" src="https://i.imgur.com/I8Pvdav.png" width="60%" ></img></center>

        <br>

        <font size="3"> Moseca utilizes state-of-the-art AI technology to extract voice or music from
        your original songs accurately. </font>

        <br>

        ### Karaoke Fun

        <center><img title="Karaoke Fun" src="https://i.imgur.com/nsn3JGV.png" width="60%" ></img></center>

        <br>

        <font size="3"> Engage with your favorite tunes in a whole new way! </font>

        <font size="3"> Moseca offers an immersive online karaoke experience, allowing you to search
        for any song on YouTube and remove the vocals online. </font>

        <font size="3"> Enjoy singing along with high-quality instrumentals at the comfort of your home.
        </font>

        <br>

        ### Easy Deployment


        <font size="3"> With Moseca, you can deploy your personal Moseca app in the
        <a href="https://huggingface.co/spaces/fabiogra/moseca?duplicate=true">
        <img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue"
        alt="Hugging Face Spaces"></a> or locally with </font>
        [![Docker Call](https://img.shields.io/badge/-Docker%20Image-blue?logo=docker&labelColor=white)](https://huggingface.co/spaces/fabiogra/moseca/discussions?docker=true)
        <font size="3"> in just one click.

        Speed up the music separation process with ready-to-use
        [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ODoK3VXajprNbskqy7G8P1h-Zom92TMA?usp=sharing)
        with GPU support.</font>

        <br>

        ### Open-Source and Free

        <font size="3"> Moseca is the free and open-source alternative to lalal.ai, splitter.ai or media.io vocal remover.

        You can modify, distribute, and use it free of charge. I believe in the power of community
        collaboration and encourage users to contribute to our source code, making Moseca better with
        each update.
        </font>

        <br>

        ### Support

        - <font size="3"> Show your support by giving a star to the GitHub repository</font> [![GitHub stars](https://img.shields.io/github/stars/fabiogra/moseca.svg?style=social&label=Star)](https://github.com/fabiogra/moseca).
        - <font size="3"> If you have found an issue or have a suggestion to improve Moseca, you can open an</font> [![GitHub issues](https://img.shields.io/github/issues/fabiogra/moseca.svg)](https://github.com/fabiogra/moseca/issues/new)
        - <font size="3"> Enjoy Moseca?</font> [![Buymeacoffee](https://img.shields.io/badge/Buy%20me%20a%20coffee--yellow.svg?logo=buy-me-a-coffee&logoColor=orange&style=social)](https://www.buymeacoffee.com/fabiogra)

        ------

        ## FAQs

        ### What is Moseca?

        <font size="3"> Moseca is an open-source web app that utilizes advanced AI technology to separate vocals and
        instrumentals from music tracks. It also provides an online karaoke experience by allowing you
        to search for any song on YouTube and remove the vocals.</font>

        ### Are there any limitations?
        <font size="3">Yes, in this environment there are some limitations regarding lenght processing
        and CPU usage to allow a smooth experience for all users.
        <b>If you want to remove these limitations you can deploy a Moseca app in your personal
        environment like in the <a href="https://huggingface.co/spaces/fabiogra/moseca?duplicate=true"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue" alt="Hugging Face Spaces"></a> or locally with [![Docker Call](https://img.shields.io/badge/-Docker%20Image-blue?logo=docker&labelColor=white)](https://huggingface.co/spaces/fabiogra/moseca/discussions?docker=true)

        You can also speed up the music separation process by [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ODoK3VXajprNbskqy7G8P1h-Zom92TMA?usp=sharing) with GPU support.</b>
        </font>


        ### How does Moseca work?
        <font size="3"> Moseca utilizes the Hybrid Spectrogram and Waveform Source Separation ([DEMUCS](https://github.com/facebookresearch/demucs)) model from Facebook. For fast karaoke vocal removal, Moseca uses the AI vocal remover developed by [tsurumeso](https://github.com/tsurumeso/vocal-remover).
        </font>
        ### How do I use Moseca?
        <font size="3">1. Upload your file: choose your song and upload it to Moseca. It supports
        a wide range of music formats for your convenience.</font>

        <font size="3">2. Choose separation mode: opt for voice only, 4-stem or 6-stem separation
        depending on your requirement.</font>

        <font size="3">3. Let AI do its magic: Moseca’s advanced AI will work to separate vocals
        from music in a matter of minutes, giving you high-quality, separated audio tracks.</font>

        <font size="3">4. Download and enjoy: preview and download your separated audio tracks.
        Now you can enjoy them anytime, anywhere! </font>
        </font>

        ### Where can I find the code for Moseca?

        <font size="3">The code for Moseca is readily available on
        [GitHub](https://github.com/fabiogra/moseca) and
        [Hugging Face](https://huggingface.co/spaces/fabiogra/moseca).
        </font>

        ### How can I get in touch with you?

        <font size="3">For any questions or feedback, feel free to contact me on </font>
        [![Twitter](https://badgen.net/badge/icon/twitter?icon=twitter&label)](https://twitter.com/grsFabio)
        <font size="3">or</font> [LinkedIn](https://www.linkedin.com/in/fabio-grasso/en).

        ------
        ## Disclaimer

        <font size="3">Moseca is designed to separate vocals and instruments from copyrighted music for
        legally permissible purposes, such as learning, practicing, research, or other non-commercial
        activities that fall within the scope of fair use or exceptions to copyright. As a user, you are
        responsible for ensuring that your use of separated audio tracks complies with the legal
        requirements in your jurisdiction.
        </font>

        </center>
        """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    header(logo_and_title=False)
    body()
    footer()
    delete_old_files("/tmp", 60 * 30)
