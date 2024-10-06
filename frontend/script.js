let selectedSprintId = null;  // Variable to store selected sprint ID

document.getElementById('searchBoardInput').addEventListener('focus', function() {
    // Clear the datalist before fetching boards to avoid duplicates
    const datalist = document.getElementById('boardsList');
    datalist.innerHTML = '';  // Clear previous options

    // Fetch boards from the API whenever the input is focused
    fetch('http://127.0.0.1:5000/api/boards')
        .then(response => response.json())
        .then(data => {
            data.forEach(board => {
                let option = document.createElement('option');
                option.value = board.name;  // Display the board name in the list
                option.dataset.boardId = board.id;  // Store board ID in data attribute
                datalist.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching boards:', error);
            alert('Failed to load boards. Please try again later.');
        });
});

// Event listener to display selected board info and fetch sprints
document.getElementById('searchBoardInput').addEventListener('change', function() {
    const selectedBoardName = this.value;
    const selectedBoardOption = [...document.getElementById('boardsList').options].find(option => option.value === selectedBoardName);
    const selectedBoardId = selectedBoardOption ? selectedBoardOption.dataset.boardId : 'Not found';



    // Enable the sprints dropdown once a board is selected
    const sprintsDropdown = document.getElementById('sprintsDropdown');
    sprintsDropdown.disabled = false;

    // Fetch sprints for the selected board
    fetchSprints(selectedBoardId);
});

// Function to fetch sprints and populate the sprint dropdown
function fetchSprints(boardId) {
    const sprintsDropdown = document.getElementById('sprintsDropdown');
    sprintsDropdown.innerHTML = '<option value="" disabled selected>Select a sprint</option>'; // Clear previous sprints
    selectedSprintId = null;  // Reset selected sprint ID
    document.getElementById('downloadPptButton').disabled = true;  // Disable the button until a sprint is selected

    fetch(`http://127.0.0.1:5000/api/boards/${boardId}/sprints`)
        .then(response => response.json())
        .then(data => {
            data.forEach(sprint => {
                let option = document.createElement('option');
                option.value = sprint.id;
                option.textContent = sprint.name;
                sprintsDropdown.appendChild(option);
            });

            // Enable event listener for the sprints dropdown
            sprintsDropdown.addEventListener('change', function() {
                selectedSprintId = this.value;  // Store selected sprint ID
                document.getElementById('downloadPptButton').disabled = false;  // Enable the download button
            });
        })
        .catch(error => {
            console.error('Error fetching sprints:', error);
            alert('Failed to load sprints. Please try again later.');
        });
}

// Event listener for download button to trigger the API call to download the PPT
document.getElementById('downloadPptButton').addEventListener('click', function() {
    if (selectedSprintId) {
        window.location.href = `http://127.0.0.1:5000/api/ppt/${selectedSprintId}`;  // Redirect to download PPT for selected sprint
    }
});