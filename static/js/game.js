// API configuration
const API_BASE_URL = 'http://localhost:5000';

// Game state
let gameState = {
    party: [],
    currentLevel: 1,
    dungeon: null,
    inCombat: false,
    combat: null
};

// Character creation state
let characterCreationState = {
    currentCharIndex: 0,
    characters: Array(4).fill(null),
    pointsRemaining: 5,
    baseAbilities: {}
};

// DOM Elements
const asciiMap = document.getElementById('ascii-map');
const messageLog = document.getElementById('messages');
const characterSheets = document.querySelectorAll('.character-sheet');
const combatInterface = document.getElementById('combat-interface');
const charCreationModal = document.getElementById('character-creation');
const charCreationForm = document.getElementById('char-creation-form');

// Event Listeners
document.getElementById('new-game').addEventListener('click', startNewGame);
document.getElementById('save-game').addEventListener('click', saveGame);
document.getElementById('load-game').addEventListener('click', loadGame);
charCreationForm.addEventListener('submit', createCharacter);

// Add event listeners for race and class selection
document.getElementById('char-race').addEventListener('change', updateAvailableClasses);
document.getElementById('char-class').addEventListener('change', updateAvailableRaces);

// Initialize game
function init() {
    // Add keyboard controls
    document.addEventListener('keydown', handleKeyPress);
    
    // Initialize character sheets
    updateCharacterSheets();
    
    // Initialize tab switching
    initializeTabs();
}

// Initialize tab switching
function initializeTabs() {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const characterSheet = button.closest('.character-sheet');
            const tabId = button.getAttribute('data-tab');
            
            // Deactivate all tabs in this character sheet
            characterSheet.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            characterSheet.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Activate clicked tab
            button.classList.add('active');
            characterSheet.querySelector(`#${tabId}`).classList.add('active');
        });
    });
}

// Start new game
async function startNewGame() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Show party creation options
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <h2>Create New Party</h2>
                    <div class="button-group">
                        <button id="generate-party">Generate Full Party</button>
                        <button id="create-custom">Create Custom Party</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Add event listeners
            document.getElementById('generate-party').addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/party/generate`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        gameState.party = data.party;
                        updateCharacterSheets();
                        modal.remove();
                        startDungeon();
                    } else {
                        addMessage('Error generating party');
                    }
                } catch (error) {
                    addMessage('Error: ' + error.message);
                }
            });

            document.getElementById('create-custom').addEventListener('click', () => {
                modal.remove();
                showCharacterCreation();
            });
        } else {
            addMessage('Error starting new game');
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

// Initialize character creation
function showCharacterCreation() {
    charCreationModal.classList.remove('hidden');
    updateCharacterNumber();
    rollAbilities();
    updateNavigationButtons();
    updateAvailableClasses();
    updateAvailableRaces();
}

function updateCharacterNumber() {
    document.getElementById('char-number').textContent = characterCreationState.currentCharIndex + 1;
}

function updateNavigationButtons() {
    const prevButton = document.getElementById('prev-char');
    const nextButton = document.getElementById('next-char');
    
    prevButton.disabled = characterCreationState.currentCharIndex === 0;
    nextButton.disabled = characterCreationState.currentCharIndex === 3 || 
                         !characterCreationState.characters[characterCreationState.currentCharIndex];
}

function rollAbilities() {
    const abilities = ['str', 'int', 'wis', 'dex', 'con', 'cha'];
    characterCreationState.baseAbilities = {};
    
    abilities.forEach(ability => {
        const score = Math.floor(Math.random() * 15) + 5; // Random between 5-19
        characterCreationState.baseAbilities[ability] = score;
        document.getElementById(ability).value = score;
    });
    
    characterCreationState.pointsRemaining = 5;
    updatePointsDisplay();
    updateAbilityButtons();
}

function updatePointsDisplay() {
    document.getElementById('points-left').textContent = characterCreationState.pointsRemaining;
}

function updateAbilityButtons() {
    const abilities = ['str', 'int', 'wis', 'dex', 'con', 'cha'];
    abilities.forEach(ability => {
        const input = document.getElementById(ability);
        const increaseBtn = input.nextElementSibling;
        const decreaseBtn = increaseBtn.nextElementSibling;
        
        const currentValue = parseInt(input.value);
        const baseValue = characterCreationState.baseAbilities[ability];
        
        increaseBtn.disabled = characterCreationState.pointsRemaining <= 0 || currentValue >= 18;
        decreaseBtn.disabled = currentValue <= baseValue;
    });
}

// Event Listeners for character creation
document.getElementById('reroll-abilities').addEventListener('click', rollAbilities);

document.querySelectorAll('.ability-increase').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.previousElementSibling;
        const currentValue = parseInt(input.value);
        if (currentValue < 18 && characterCreationState.pointsRemaining > 0) {
            input.value = currentValue + 1;
            characterCreationState.pointsRemaining--;
            updatePointsDisplay();
            updateAbilityButtons();
        }
    });
});

document.querySelectorAll('.ability-decrease').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.previousElementSibling.previousElementSibling;
        const currentValue = parseInt(input.value);
        const baseValue = characterCreationState.baseAbilities[input.id];
        if (currentValue > baseValue) {
            input.value = currentValue - 1;
            characterCreationState.pointsRemaining++;
            updatePointsDisplay();
            updateAbilityButtons();
        }
    });
});

document.getElementById('prev-char').addEventListener('click', () => {
    if (characterCreationState.currentCharIndex > 0) {
        characterCreationState.currentCharIndex--;
        updateCharacterNumber();
        loadCharacterData();
        updateNavigationButtons();
    }
});

document.getElementById('next-char').addEventListener('click', () => {
    if (characterCreationState.currentCharIndex < 3) {
        characterCreationState.currentCharIndex++;
        updateCharacterNumber();
        loadCharacterData();
        updateNavigationButtons();
    }
});

function loadCharacterData() {
    const character = characterCreationState.characters[characterCreationState.currentCharIndex];
    if (character) {
        document.getElementById('char-name').value = character.name;
        document.getElementById('char-race').value = character.race;
        document.getElementById('char-class').value = character.characterClass;
        
        const abilities = ['str', 'int', 'wis', 'dex', 'con', 'cha'];
        abilities.forEach(ability => {
            document.getElementById(ability).value = character.abilities[ability.toUpperCase()];
        });
        
        characterCreationState.baseAbilities = { ...character.abilities };
        characterCreationState.pointsRemaining = 0;
        updatePointsDisplay();
        updateAbilityButtons();
    } else {
        charCreationForm.reset();
        rollAbilities();
    }
}

// Function to update available classes based on race selection
function updateAvailableClasses() {
    const raceSelect = document.getElementById('char-race');
    const classSelect = document.getElementById('char-class');
    const selectedRace = raceSelect.value;
    
    // Get all class options
    const classOptions = Array.from(classSelect.options);
    
    // Check each class against racial restrictions
    classOptions.forEach(option => {
        const isRestricted = (
            (selectedRace === 'Lizardfolk' && option.value === 'Paladin') ||
            (selectedRace === 'Goblin' && option.value === 'Paladin')
        );
        
        option.disabled = isRestricted;
        
        // If current selection is now invalid, select first valid option
        if (isRestricted && classSelect.value === option.value) {
            const firstValidOption = classOptions.find(opt => !opt.disabled);
            if (firstValidOption) {
                classSelect.value = firstValidOption.value;
            }
        }
    });
}

// Function to update available races based on class selection
function updateAvailableRaces() {
    const raceSelect = document.getElementById('char-race');
    const classSelect = document.getElementById('char-class');
    const selectedClass = classSelect.value;
    
    // Get all race options
    const raceOptions = Array.from(raceSelect.options);
    
    // Check each race against class restrictions
    raceOptions.forEach(option => {
        const isRestricted = (
            (selectedClass === 'Paladin' && (option.value === 'Lizardfolk' || option.value === 'Goblin'))
        );
        
        option.disabled = isRestricted;
        
        // If current selection is now invalid, select first valid option
        if (isRestricted && raceSelect.value === option.value) {
            const firstValidOption = raceOptions.find(opt => !opt.disabled);
            if (firstValidOption) {
                raceSelect.value = firstValidOption.value;
            }
        }
    });
}

// Update the createCharacter function to include race in class requirements check
async function createCharacter(event) {
    event.preventDefault();
    
    // Check if party is already full
    if (gameState.party.length >= 4) {
        addMessage('Party is already full (maximum 4 characters)');
        return;
    }
    
    const formData = {
        name: document.getElementById('char-name').value,
        race: document.getElementById('char-race').value,
        characterClass: document.getElementById('char-class').value,
        abilities: {
            STR: parseInt(document.getElementById('str').value),
            INT: parseInt(document.getElementById('int').value),
            WIS: parseInt(document.getElementById('wis').value),
            DEX: parseInt(document.getElementById('dex').value),
            CON: parseInt(document.getElementById('con').value),
            CHA: parseInt(document.getElementById('cha').value)
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/character/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const character = await response.json();
            gameState.party.push(character);
            characterCreationState.characters[characterCreationState.currentCharIndex] = character;
            updateCharacterSheets();
            
            if (gameState.party.length === 4) {
                charCreationModal.classList.add('hidden');
                startDungeon();
            } else {
                characterCreationState.currentCharIndex++;
                updateCharacterNumber();
                charCreationForm.reset();
                rollAbilities();
                updateNavigationButtons();
                // Initialize race/class restrictions
                updateAvailableClasses();
                updateAvailableRaces();
            }
        } else {
            const error = await response.json();
            addMessage(error.error || 'Error creating character');
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

// Update character sheets
function updateCharacterSheets() {
    console.log("Updating character sheets...");  // Debug log
    console.log("Current game state:", gameState);  // Debug log
    
    characterSheets.forEach((sheet, index) => {
        const character = gameState.party[index];
        console.log(`Character ${index}:`, character);  // Debug log
        
        if (character) {
            const statsDiv = sheet.querySelector('.char-stats');
            const inventoryDiv = sheet.querySelector('.char-inventory');
            const skillsDiv = sheet.querySelector('.char-skills');
            
            // Calculate ability modifiers
            const abilityModifiers = {};
            Object.entries(character.abilities).forEach(([ability, score]) => {
                abilityModifiers[ability] = Math.floor((score - 10) / 2);
            });

            // Format money             
            const formatMoney = (character) => {
                const gold = character.gold || 0;
                const silver = character.silver || 0;
                const copper = character.copper || 0;
                return `${gold}g ${silver}s ${copper}c`;
            };

            // Initial render with placeholder for XP
            statsDiv.innerHTML = `
                <div class="basic-info">
                    <p>Name: ${character.name}</p>
                    <p>Race: ${character.race}</p>
                    <p>Class: ${character.characterClass}</p>
                    <p>Level: ${character.level}</p>
                    <p>Experience: ${character.experience}</p>
                    <p>Next Level: Calculating...</p>
                    <p>Money: ${formatMoney(character)}</p>
                </div>
                <div class="combat-stats">
                    <p>HP: ${character.hitPoints}/${character.maxHitPoints}</p>
                    <p>AC: ${character.armorClass}</p>
                    <p>THAC0: ${character.thac0}</p>
                </div>
                <div class="ability-scores">
                    <h4>Ability Scores</h4>
                    ${Object.entries(character.abilities).map(([ability, score]) => `
                        <p>${ability}: ${score} (${abilityModifiers[ability] >= 0 ? '+' : ''}${abilityModifiers[ability]})</p>
                    `).join('')}
                </div>
                <div class="saving-throws">
                    <h4>Saving Throws</h4>
                    ${Object.entries(character.savingThrows || {})
                        .map(([save, value]) => `<p>${save}: ${value}</p>`).join('')}
                </div>
            `;
            
            inventoryDiv.innerHTML = `
                <div class="equipment">
                    <h4>Equipment</h4>
                    <ul>
                        ${Object.entries(character.equipment)
                            .map(([slot, item]) => `<li>${slot}: ${item ? item.name : 'None'}</li>`)
                            .join('')}
                    </ul>
                </div>
                <div class="inventory">
                    <h4>Inventory</h4>
                    <ul>
                        ${character.inventory ? character.inventory
                            .map(item => `<li>${item.name}${item.quantity > 1 ? ` (${item.quantity})` : ''}</li>`)
                            .join('') : '<li>No items</li>'}
                    </ul>
                </div>
            `;
            
            console.log("Character spells:", character.spells);  // Debug log
            console.log("Character spell slots:", character.spellSlots);  // Debug log
            
            skillsDiv.innerHTML = `
                <div class="skills">
                    <h4>Skills</h4>
                    <ul>
                        ${character.skills ? Object.entries(character.skills)
                            .map(([skill, level]) => `<li>${skill} <span class="skill-level">${level}</span></li>`)
                            .join('') : '<li>No skills</li>'}
                    </ul>
                </div>
                <div class="spells">
                    <h4>Spell Book</h4>
                    ${character.spells ? Object.entries(character.spells)
                        .map(([level, spells]) => `
                            <div class="spell-level">
                                <h5>Level ${level} (${character.spellSlots?.[level] || 0} slots)</h5>
                                <ul>
                                    ${spells.map(spell => `
                                        <li>
                                            ${spell.name}
                                            ${spell.memorized ? ' (Memorized)' : ''}
                                            ${spell.cast ? ' (Cast)' : ''}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        `).join('') : '<p>No spells</p>'}
                </div>
            `;

            // Fetch XP needed for next level
            fetchXPRequirement(character, statsDiv);
        } else {
            sheet.querySelector('.char-stats').innerHTML = '<p>No character</p>';
            sheet.querySelector('.char-inventory').innerHTML = '';
            sheet.querySelector('.char-skills').innerHTML = '';
        }
    });
}

async function fetchXPRequirement(character, statsDiv) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/rules/xp-for-level`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                characterClass: character.characterClass,
                level: character.level
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const nextLevelElement = statsDiv.querySelector('.basic-info p:nth-child(6)');
        if (nextLevelElement) {
            nextLevelElement.textContent = `Next Level: ${data.xp}`;
        }
    } catch (error) {
        console.error('Error fetching XP requirement:', error);
        const nextLevelElement = statsDiv.querySelector('.basic-info p:nth-child(6)');
        if (nextLevelElement) {
            nextLevelElement.textContent = 'Next Level: Error loading';
        }
    }
}

// Dungeon generation and movement
async function startDungeon() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/state`);
        if (response.ok) {
            gameState = await response.json();
            renderDungeon();
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

function renderDungeon() {
    if (!gameState.dungeon) return;
    
    let mapString = '';
    for (let y = 0; y < gameState.dungeon.length; y++) {
        for (let x = 0; x < gameState.dungeon[y].length; x++) {
            const tile = gameState.dungeon[y][x];
            const span = document.createElement('span');
            
            // Check if this position has a party member
            const partyMember = gameState.party.find(char => 
                char.position.x === x && char.position.y === y
            );
            
            if (partyMember) {
                span.textContent = '@';
                span.style.color = getClassColor(partyMember.characterClass);
                span.title = partyMember.name;
                span.style.cursor = 'help';
            } else if (!tile.visible) {
                span.textContent = ' ';
                span.style.color = '#000000';
                span.style.backgroundColor = '#000000';
            } else {
                span.textContent = tile.char;
                span.style.color = tile.color;
                
                // Add tooltip for monsters
                if (tile.monster_data) {
                    span.title = tile.monster_data.name;
                    span.style.cursor = 'help';
                }
            }
            
            asciiMap.appendChild(span);
        }
        asciiMap.appendChild(document.createElement('br'));
    }
}

// Helper function to get class color
function getClassColor(characterClass) {
    const classColors = {
        'Fighter': '#ff0000',    // Red
        'Magic-User': '#0000ff', // Blue
        'Cleric': '#ffff00',     // Yellow
        'Thief': '#00ff00',      // Green
        'Ranger': '#ffa500',     // Orange
        'Paladin': '#ff00ff',    // Magenta
        'Druid': '#008000',      // Dark Green
        'Illusionist': '#800080', // Purple
        'Bard': '#00ffff'        // Cyan
    };
    return classColors[characterClass] || '#ffffff';
}

function updateMap() {
    // Clear the map
    asciiMap.innerHTML = '';
    
    // Get party position (assuming first character's position)
    const partyX = gameState.party[0].position.x;
    const partyY = gameState.party[0].position.y;
    
    // Render the updated map
    renderDungeon();
}

// Movement handling
function handleKeyPress(event) {
    if (gameState.inCombat) return;
    
    let direction = '';
    switch (event.key) {
        case 'ArrowUp':
        case 'w':
            direction = 'north';
            break;
        case 'ArrowDown':
        case 's':
            direction = 'south';
            break;
        case 'ArrowLeft':
        case 'a':
            direction = 'west';
            break;
        case 'ArrowRight':
        case 'd':
            direction = 'east';
            break;
        default:
            return;
    }
    
    moveParty(direction);
}

async function moveParty(direction) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ direction })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                gameState = result.gameState;
                updateMap();
                updateCharacterSheets();
            }
            if (result.message) {
                addMessage(result.message);
            }
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

// Combat handling
function startCombat(monsters) {
    gameState.inCombat = true;
    gameState.combat = {
        monsters,
        currentTurn: 0,
        initiative: []
    };
    
    combatInterface.classList.remove('hidden');
    rollInitiative();
}

async function handleCombatAction(action) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/combat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.message) {
                addMessage(result.message);
            }
            if (result.combatEnded) {
                endCombat();
            }
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

function endCombat() {
    gameState.inCombat = false;
    gameState.combat = null;
    combatInterface.classList.add('hidden');
    updateCharacterSheets();
}

// Utility functions
function addMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageLog.appendChild(messageElement);
    // Ensure scroll to bottom happens after the DOM update    
    messageLog.scrollTop = messageLog.scrollHeight;    
}

async function saveGame() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(gameState)
        });
        
        if (response.ok) {
            addMessage('Game saved successfully');
        } else {
            addMessage('Error saving game');
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

async function loadGame() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/game/load`);
        if (response.ok) {
            gameState = await response.json();
            updateCharacterSheets();
            updateMap();
        }
    } catch (error) {
        addMessage('Error: ' + error.message);
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', init); 