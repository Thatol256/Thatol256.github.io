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
			
			status.textContent = user.completion
			title.textContent = user.title
			difficulty.textContent = user.difficulty
			catagory.textContent = user.catagory
			date.textContent = user.date
			tags.textContent = user.tags
			
			userCardContainer.append(card)
			return { completion:user.completion, title:user.title, difficulty:user.difficulty, catagory:user.catagory, date:user.date, tags:user.tags, element:card }
		})
	})