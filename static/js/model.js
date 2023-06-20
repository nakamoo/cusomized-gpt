// Initialization
const form = document.querySelector(".gpt_form-block");
let isFirstSubmit = true;
// Launch the function when the form is submitted
form.addEventListener("submit", event => {
  event.preventDefault();
  // Function that scrolls through the conversation when the form is sent
  setTimeout(function () {
    const gptContentAnswer = document.querySelector('.gpt_content-answer');
    gptContentAnswer.scrollTop += 20000;
  }, 100);
  // Get the query entered by the user in the form
  const inputValue = document.querySelector(".gpt_input").value;
  // If the form is sent, then we hide the home screen and display the conversation
  if (isFirstSubmit) {
    document.querySelector(".gpt_content-top").style.display = "none";
    document.querySelector(".gpt_content-answer").style.display = "flex";
    // document.querySelector(".gpt_nav_conversation").style.display = "flex";
    isFirstSubmit = false;
  }
  // Collect all data (collection list .gpt_collection-list)
  const collectionList = document.querySelectorAll(".gpt_collection-item");
  // Loop through the data to find the right answer
  /*
  let matchingAnswer = "Sorry, my database can't provide an answer to your query, but you can try to make a request about Figma or Webflow. For example: How to become a Figma expert ? or How to become a Webflow expert ?";
  let bestMatch = 0;
  const inputWords = inputValue.toLowerCase().split(" ");
  for (let i = 0; i < collectionList.length; i++) {
    const keywords = collectionList[i].querySelector(".gpt_collection-keywords").innerText.toLowerCase();
    const keywordWords = keywords.split(" ");
    const answer = collectionList[i].querySelector(".gpt_collection-answer").innerHTML;
    const answerWords = answer.toLowerCase().split(" ");
    // Calculate Jaccard similarity between input and keywords
    const keywordSimilarity = jaccard(inputWords, keywordWords);
    // Calculate Jaccard similarity between input and answer
    const answerSimilarity = jaccard(inputWords, answerWords);
    // Keep track of the item with the best match
    if (keywordSimilarity + answerSimilarity > bestMatch) {
      bestMatch = keywordSimilarity + answerSimilarity;
      matchingAnswer = answer;
    }
  }
*/
  // Jaccard Function
  function jaccard(a, b) {
    const aSet = new Set(a);
    const bSet = new Set(b);
    const union = new Set([...aSet, ...bSet]);
    const intersection = new Set([...aSet].filter(x => bSet.has(x)));
    return intersection.size / union.size;
  }
  // Adds the user's request to the conversation
  const lightMode1 = document.querySelector(".icon-1x1-semimedium.is-light-mode");
  const classList = lightMode1.style.display === "none" ? "is-light" : "is-dark";
  const line1 = document.createElement("div");
  line1.classList.add("gpt_content-line", classList);
  const wrapper = document.createElement("div");
  wrapper.classList.add("gpt_content-wrapper");
  line1.appendChild(wrapper);
  const img = document.createElement("img");
  img.src = "https://uploads-ssl.webflow.com/63da865e4dca1b4866173120/63da87244dca1b63df174041_image-people.webp";
  img.loading = "lazy";
  img.sizes = "100vw";
  img.alt = "a person with a blue body";
  img.classList.add("gpt_image");
  wrapper.appendChild(img);
  const text = document.createElement("div");
  text.classList.add("gpt_content-text", classList);
  text.innerHTML = inputValue;
  wrapper.appendChild(text);
  document.querySelector(".gpt_content-answer").appendChild(line1);
  // If a matching answer is found, add the answer and the HTML structure in the rich text
  function addChatLine(mode) {
    const line = document.createElement("div");
    line.classList.add("gpt_content-line", "is-bot", mode);
    const wrapper = document.createElement("div");
    wrapper.classList.add("gpt_content-wrapper");
    line.appendChild(wrapper);
    const img = document.createElement("img");
    img.src = "https://uploads-ssl.webflow.com/63da865e4dca1b4866173120/63da87244dca1b6000174040_Power-vert.svg";
    img.loading = "lazy";
    img.alt = "Webflow GPT";
    img.classList.add("gpt_image");
    wrapper.appendChild(img);
    const text = document.createElement("div");
    text.classList.add("gpt_content-text", "gpt_content-text-answer", mode);
    wrapper.appendChild(text);
    const gptNavConversationContentText = document.querySelectorAll(".gpt_nav_conversation-content-text");
    document.querySelector(".gpt_content-answer").appendChild(line);
    gptNavConversationContentText.forEach((element) => {
      element.innerHTML = inputValue;
      element.classList.remove('gpt_nav_conversation-content-text');
    });
    return text;
  }
  /*
    if (matchingAnswer) {
      if (lightMode1.style.display === "none") {
        addChatLine("is-light", matchingAnswer);
      } 
      else {
        addChatLine("is-dark", matchingAnswer);
      }
    }
    */
  function showRow() {
    if (lightMode1.style.display === "none") {
      return addChatLine("is-light");
    }
    else {
      return addChatLine("is-dark");
    }
  }
  function showAnswer(text_obj, answer) {
    var typed = new Typed(text_obj, {
      strings: [answer],
      typeSpeed: 10,
      loop: false
    });
  }

  var text_obj = showRow();
  $("#Question").val("");

  $.ajax({
    type: 'POST',
    url: '/query',
    data: JSON.stringify({ "query": inputValue, "index_id": $("#indexId").text() }),
    contentType: 'application/json',
    success: function (responseData, status) {
      console.log(responseData.answer);
      showAnswer(text_obj, responseData.answer);
    },
    error: function (jqXHR, status, error) {
      showAnswer(text_obj, "Sorry, something went wrong. Please try again later.");
    },
  });
});
// This function is used to switch between light and dark modes.
function switchModes() {
  // Select the light mode icon
  const lightMode = document.querySelector(".icon-1x1-semimedium.is-light-mode");
  // Select the dark mode icon
  const darkMode = document.querySelector(".icon-1x1-semimedium.is-dark-mode");
  // Select the text that displays the mode
  const modeText = document.querySelector("#ld-mode div:last-child");
  // Select all header elements
  const headers = document.querySelectorAll("h1, h2");
  // Select all elements with class "is-light"
  const lightElements = document.querySelectorAll(".is-light");
  // Select all elements with class "is-dark"
  const darkElements = document.querySelectorAll(".is-dark");
  // The color for light mode
  const lightColor = "#FFFFFF";
  // The color for dark mode
  const darkColor = "#202123";
  // Check if light mode icon is not being displayed
  if (lightMode.style.display === "none") {
    // Show light mode icon and hide dark mode icon
    lightMode.style.display = "block";
    darkMode.style.display = "none";
    // Update mode text to "Light mode"
    modeText.innerHTML = "Light mode";
    // Set color of headers to lightColor
    headers.forEach(header => {
      header.style.color = lightColor;
    });
    // Replace class "is-light" with "is-dark" for light elements
    lightElements.forEach(element => {
      element.classList.replace("is-light", "is-dark");
    });
  } else {
    // Show dark mode icon and hide light mode icon
    lightMode.style.display = "none";
    darkMode.style.display = "block";
    // Update mode text to "Dark mode"
    modeText.innerHTML = "Dark mode";
    // Set color of headers to darkColor
    headers.forEach(header => {
      header.style.color = darkColor;
    });
    // Replace class "is-dark" with "is-light" for dark elements
    darkElements.forEach(element => {
      element.classList.replace("is-dark", "is-light");
    });
  }
}
// Call switchModes function when the element with id "ld-mode" is clicked
document.querySelector("#ld-mode").addEventListener("click", switchModes);
$(document).ready(function () {
  switchModes();
});