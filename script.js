const userCardTemplate = document.querySelector("[docListing]") //template
const userCardContainer = document.querySelector("[docContainer]") //container of the doc objects
const searchInput = document.querySelector("[searchBar]")

let users = []

searchInput.addEventListener("input", e => {
	const value = e.target.value.toLowerCase()
	users.forEach(user => {
		var isVisible =
			user.title.toLowerCase().includes(value) ||
			user.difficulty.toLowerCase().includes(value) ||
			user.catagory.toLowerCase().includes(value) ||
			user.date.toLowerCase().includes(value)
		user.tags.forEach(tag => {
			if (tag.toLowerCase().includes(value)) {
				isVisible = true;
			}
		})
		user.element.classList.toggle("hide", !isVisible)
	})
})

fetch("pages.json")
	.then(res => res.json())
	.then(data => {
		users = data.map(user => {
			const card = userCardTemplate.content.cloneNode(true).children[0]
			
			//for each attribute in the template
			const status = card.querySelector("[docStatus]")
			const title = card.querySelector("[docTitle]")
			const difficulty = card.querySelector("[docDifficulty]")
			const catagory = card.querySelector("[docCatagory]")
			const date = card.querySelector("[docDate]")
			const tags = card.querySelector("[docTags]")
			
			var color = "white";
			var text = "Error: Completion attribute is invalid.";
			if (user.completion == "Complete") { color = "green"; text = "This page is complete."; } //complete, not active
			else if (user.completion == "Incomplete") { color = "yellow"; text = "This page is incomplete, but is still being worked on."; } //incomplete, active
			else if (user.completion == "Gone") { color = "red"; text = "This page has not been created yet."; }
			else if (user.completion == "Abandoned") { color = "orange"; text = "This page has been abandoned in an incomplete state."; } //incomplete, not active
			else if (user.completion == "Ongoing") { color = "lime"; text = "This page is of a complete project that is still being worked on."; } //complete, active
			
			var difficultyColor = "white";
			if (user.difficulty == "Easy") { difficultyColor = "green"; }
			else if (user.difficulty == "Normal") { difficultyColor = "lime"; }
			else if (user.difficulty == "Hard") { difficultyColor = "yellow"; }
			else if (user.difficulty == "Very hard") { difficultyColor = "orange"; }
			else if (user.difficulty == "Brutal") { difficultyColor = "red"; }
			
			status.setAttribute("id", color)
			status.setAttribute("title", text)
			title.textContent = user.title
			title.setAttribute("href", user.ref)
			difficulty.textContent = user.difficulty
			difficulty.setAttribute("id", difficultyColor)
			catagory.textContent = user.catagory
			date.textContent = user.date
			tags.textContent = user.tags
			
			userCardContainer.append(card)
			return { ref:user.ref, completion:user.completion, title:user.title, difficulty:user.difficulty, catagory:user.catagory, date:user.date, tags:user.tags, element:card }
		})
	})