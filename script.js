//https://vid.puffyan.us/watch?v=TlP5WIxVirU

const userCardTemplate = document.querySelector("[docListing]") //template
const userCardContainer = document.querySelector("[docContainer]") //container of the doc objects
const searchInput = document.querySelector("[searchBar]")

let users = []

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
			
			var color = "color:#FFFFFF";
			var text = "Error: Completion attribute is invalid.";
			if (user.completion == "complete") { color = "color:#00FF00"; text = "This page is complete."; }
			else if (user.completion == "incomplete") { color = "color:#FFFF00"; text = "This page is incomplete."; }
			else if (user.completion == "gone") { color = "color:#FF0000"; text = "This page has not been created yet."; }
			
			var difficultyColor = "color:#FFFFFF";
			if (user.difficulty == "Easy") { color = "color:#009900"; }
			else if (user.difficulty == "Normal") { color = "color:#99FF33"; }
			else if (user.difficulty == "Hard") { color = "color:#FFFF00"; }
			else if (user.difficulty == "Very hard") { color = "color:#FF6600"; }
			else if (user.difficulty == "Brutal") { color = "color:#FF0000"; }
			
			status.setAttribute("style", color)
			status.setAttribute("title", text)
			title.textContent = user.title
			difficulty.textContent = user.difficulty
			difficulty.setAttribute("style", difficultyColor)
			catagory.textContent = user.catagory
			date.textContent = user.date
			tags.textContent = user.tags
			
			userCardContainer.append(card)
			return { completion:user.completion, title:user.title, difficulty:user.difficulty, catagory:user.catagory, date:user.date, tags:user.tags, element:card }
		})
	})