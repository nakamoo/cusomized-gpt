import os
import re
import shutil
import sys


original_html_dir_path = "./original_html"


def replace_file_path(html):
    # css_paths = re.findall(r'["\']((?!http)[^"\']*\.(?:css|js|png|jpeg|svg|ico|json))["\']', html)
    # for path in css_paths:
    #     new_path = r"{{ url_for('static', filename='" + path + r"') }}"
    #     html = html.replace(path, new_path)
    html = re.sub(
        r'(["\' ])((?!http)[^"\']*?\.(?:css|js|png|jpeg|jpg|svg|ico|json))(["\' ])',
        r"\1{{ url_for('static', filename='\2') }}\3",
        html,
    )

    html = re.sub(r'href="(\S*)\.html', r'href="/\1', html)
    return html


def add_login_button(html):
    login_button_html = """
<script src="https://accounts.google.com/gsi/client" async defer></script>
<div id="g_id_onload"
     data-client_id="374799132811-4vgn7ietidmmt2b7ka2sf0l6fh04ptni.apps.googleusercontent.com"
     data-context="use"
     data-ux_mode="popup"
     data-login_uri="/login/authorized"
     data-auto_prompt="false">
</div>

<div class="g_id_signin"
     data-type="standard"
     data-shape="pill"
     data-theme="outline"
     data-text="continue_with"
     data-size="large"
     data-logo_alignment="center"
     data-width="400">
</div>
"""
    html = re.sub(
        r"##LOGIN##",
        login_button_html,
        html,
    )
    return html


def fill_templates_models(html):
    template = """
              {% if models %}
                {% for model in models %}
                    {% if model.status == ModelStatus.IN_PROGRESS %}
                        <div class="w-layout-grid grid">
                            <div id="w-node-e7790a86-f8bb-0919-6da5-28ff7a047ae4-ba3ba9a8">{{ model.name }}(作成中) </div>
                            <div id="w-node-_0c915835-4575-ff3c-8fd9-00af1664b1b1-ba3ba9a8">{{ model.created_at.strftime('%Y-%m-%d') }} </div>
                        </div>
                    {% elif model.status == ModelStatus.SUCCESS %}
                        <a href="/model/{{ model.id }}" target="_blank" class="link-block-2 w-inline-block">
                        <div class="w-layout-grid grid">
                            <div id="w-node-e7790a86-f8bb-0919-6da5-28ff7a047ae4-ba3ba9a8">{{ model.name }}</div>
                            <div id="w-node-_0c915835-4575-ff3c-8fd9-00af1664b1b1-ba3ba9a8">{{ model.created_at.strftime('%Y-%m-%d') }} </div>
                        </div>
                        </a>
                    {% endif %}
                {% endfor %}
              {% else %}
                <p>カスタマイズ済みのChatGPTはまだありません。</p>
              {% endif %}"""
    html = re.sub(r"##MODELS_HTML##", template, html)
    return html


def change_submit_function_of_model(html):
    submit_func_html = """
  function showAnswer(answer) {
  	if (lightMode1.style.display === "none") {
    	addChatLine("is-light", answer);
  	} 
    else {
    	addChatLine("is-dark", answer);
  	}
  }

  $.ajax({
    type: 'POST',
    url: '/query',
    data: JSON.stringify(inputValue),
    contentType: 'application/json',
    success: function (responseData, status) {
      showAnswer(responseData.answer);
    },
    error: function (jqXHR, status, error) {
      showAnswer("Sorry, something went wrong. Please try again later.");
    },
  });
"""
    html = re.sub(
        r"\n(\s*// Loop through.*\n)\s*// Jaccard",
        r"\t\n// Jaccard",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"(if \(matchingAnswer\) {(.*?\}){3})", submit_func_html, html, flags=re.DOTALL
    )
    return html


def prepare_html():
    original_html_dir_path = "./original_html"
    template_dir_path = "./templates"

    for dir_path, dir_names, file_names in os.walk(original_html_dir_path):
        for file_name in file_names:
            if not file_name.endswith(".html"):
                continue
            with open(os.path.join(dir_path, file_name), "r") as f:
                html = f.read()
            updated_html = replace_file_path(html)
            if file_name == "login.html":
                updated_html = add_login_button(updated_html)
            if file_name == "mypage.html":
                updated_html = fill_templates_models(updated_html)
            # if file_name == "model.html":
            #     updated_html = change_submit_function_of_model(updated_html)

            with open(os.path.join(template_dir_path, file_name), "w") as f:
                f.write(updated_html)


def move_static_files(path):
    if os.path.isdir("./static"):
        shutil.rmtree("./static/")
    os.mkdir("./static")

    for dir in ["css", "js", "images", "documents"]:
        if os.path.exists(os.path.join(path, dir)):
            shutil.copytree(os.path.join(path, dir), "./static/" + dir)

    for filename in os.listdir("./original_js/"):
        filepath = "./original_js/" + filename
        if not os.path.isfile(filepath):
            continue
        shutil.copy(filepath, "./static/js/")


def move_html_files(path):
    if os.path.isdir(original_html_dir_path):
        shutil.rmtree(original_html_dir_path + "/")
    os.mkdir(original_html_dir_path)

    for dir_path, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            if not file_name.endswith(".html"):
                continue
            shutil.copy(os.path.join(dir_path, file_name), "./original_html/")


if __name__ == "__main__":
    args = sys.argv
    move_html_files(args[1])
    move_static_files(args[1])
    prepare_html()
    # subprocess.run(["node", "parseAndChange.js"], capture_output=True)
