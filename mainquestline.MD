# Main Quest Line Documentation

## Summary Table of Key Choices

| Fork                | Choice         | Immediate Outcome                | Side Quest Unlocked      | Long-term Impact                |
|---------------------|---------------|----------------------------------|--------------------------|---------------------------------|
| Who to Trust        | Seren/Bram/Lysa| Different clues, Order secrets   | Varies                   | Sets up confrontation with Bram |
| Justice or Mercy    | Mercy         | Bram becomes ally                | Redemption's Price       | Informant, compassionate rep    |
|                     | Justice       | Artifact damaged, chaos spreads  | Shadows Unleashed        | Ruthless rep, Order cautious    |

---

## Main Quest Line Overview

The main quest line "Shadow of the Artifact" consists of a series of quests that guide the player through the game's story. Each quest is designed to integrate with the existing dialog and quest systems, with multiple decision points that influence the storyline.

## Implementation Details

### Quest Data Structure

The main quest line will be stored in a series of JSON files in the `data/quests` directory:

- `main_quests.json` - Contains the core quest data
- `main_quest_chain.json` - Defines the sequence and prerequisites
- `dialogs/main_quest_dialogs.json` - Contains the dialog scripts for NPCs

### Quest Chain Definition

The main quest chain will be registered with the QuestManager:

```python
def initialize_main_quests(quest_manager):
    # Define the main quest chain
    chain_data = {
        "name": "Shadow of the Artifact",
        "description": "Uncover the secrets of the ancient artifact and stop the spreading corruption.",
        "quests": [
            "mq_01_mysterious_arrival",
            "mq_02_first_investigation", 
            "mq_03_suspects_trail",
            "mq_04_truth_revealed",
            "mq_05_confrontation",
            "mq_06_final_choice"
        ]
    }
    
    # Register the chain
    quest_manager.add_quest_chain("main_quest_chain", chain_data, save_to_file=True)
```

## Quest Breakdown

### MQ-01: Mysterious Arrival

**Quest ID:** `mq_01_mysterious_arrival`  
**Type:** Main Quest  
**Level Requirement:** 1  
**NPC Giver:** Captain Thorne  
**Dialog ID:** `thorne_introduction`

**Description:**  
The player arrives in the town of Eldervale to find it plagued by strange occurrences. Captain Thorne, the town's guard captain, seeks the player's help to investigate.

**Objectives:**
1. Speak with Captain Thorne (Dialog Objective)
2. Visit the town square (Explore Objective)
3. Investigate the strange energy (Interact Objective)
4. Return to Captain Thorne (Dialog Objective)

**Implementation Notes:**
- Implement using existing DialogObjective class
- Create a glowing effect at the town square marking the energy
- NPC Captain Thorne should have the quest_giver flag set to true

### MQ-02: First Investigation

**Quest ID:** `mq_02_first_investigation`  
**Type:** Main Quest  
**Level Requirement:** 2  
**NPC Giver:** Captain Thorne  
**Dialog ID:** `thorne_investigation`

**Description:**  
Captain Thorne believes an ancient artifact is causing the disturbances. The player must locate and examine it.

**Objectives:**
1. Search the abandoned temple ruins (Explore Objective)
2. Defeat the corrupted guardians (Kill Objective - 3 monsters)
3. Retrieve the artifact fragment (Collect Objective)
4. Return to Captain Thorne (Dialog Objective)

**Dialog Key Points:**
- Thorne_investigation node should introduce the backstory of the artifact
- Upon completion, set up the primary suspects

### MQ-03: Suspects Trail

**Quest ID:** `mq_03_suspects_trail`  
**Type:** Main Quest  
**Level Requirement:** 3  
**NPC Giver:** Captain Thorne  
**Dialog IDs:** 
- `thorne_report`
- `seren_interrogation`
- `bram_interrogation`
- `lysa_interrogation`

**Description:**  
Three people were seen near the temple before the disturbances began: Seren (the royal scholar), Bram (a city guard), and Lysa (a traveling merchant). The player must interrogate each to determine who may be involved.

**Objectives:**
1. Talk to Seren (Dialog Objective)
2. Talk to Bram (Dialog Objective)
3. Talk to Lysa (Dialog Objective)
4. Report findings to Captain Thorne (Dialog Objective)

**Key Choice:** "Who to Trust"
- Dialog choice sets the flag `trusted_suspect=name`
- Different dialog paths and clues based on choice

### MQ-04: Truth Revealed

**Quest ID:** `mq_04_truth_revealed`  
**Type:** Main Quest  
**Level Requirement:** 4  
**NPC Giver:** Depends on trusted suspect  
**Dialog ID:** Various based on suspect

**Description:**  
Following the lead from the chosen suspect, the player discovers that the artifact is connected to an ancient order. Bram is revealed to be involved, but his motives remain unclear.

**Objectives:**
1. Follow the suspect's lead (varies based on trusted suspect)
2. Explore the hidden chamber (Explore Objective)
3. Recover the ancient text (Collect Objective)
4. Confront Bram (Dialog Objective)

**Implementation Notes:**
- Different starting objectives based on the `trusted_suspect` flag
- Bram's location should change based on previous choices

### MQ-05: Confrontation

**Quest ID:** `mq_05_confrontation`  
**Type:** Main Quest  
**Level Requirement:** 5  
**NPC Giver:** Captain Thorne  
**Dialog ID:** `thorne_final_orders`

**Description:**  
The player must confront Bram at the ancient shrine where he's attempting to unlock the artifact's power.

**Objectives:**
1. Travel to the ancient shrine (Explore Objective)
2. Defeat Bram's corrupted allies (Kill Objective - 5 monsters)
3. Confront Bram (Dialog Objective)

### MQ-06: Final Choice

**Quest ID:** `mq_06_final_choice`  
**Type:** Main Quest  
**Level Requirement:** 5  
**NPC Giver:** N/A (auto-continuation)  
**Dialog ID:** `bram_confrontation`

**Description:**  
The player learns that Bram was trying to contain the artifact's power, not unleash it. The player must choose whether to show mercy or bring Bram to justice.

**Objectives:**
1. Make your choice (Dialog Objective with branching paths)
2. Deal with the artifact (depends on choice)
3. Return to Captain Thorne (Dialog Objective)

**Key Choice:** "Justice or Mercy"
- Dialog choice sets the flag `bram_fate=justice/mercy`
- Different endings and rewards based on choice
- Unlocks different side quests

## Dialog Implementation

Sample dialog structure for a key conversation:

```json
{
  "bram_confrontation": {
    "npc_name": "Bram",
    "npc_title": "City Guard",
    "dialogs": [
      {
        "id": "initial",
        "text": [
          "You've found me. I suppose there's no hiding what I've done.",
          "But you don't understand - I was trying to contain the artifact's power, not release it."
        ],
        "choices": [
          {
            "text": "Why should I believe you?",
            "next": "explanation"
          },
          {
            "text": "You've endangered everyone!",
            "next": "defensive"
          }
        ]
      },
      {
        "id": "explanation",
        "text": [
          "The Order has protected these artifacts for generations. I am the last guardian.",
          "If the artifact's power is released, the corruption will spread across the land."
        ],
        "choices": [
          {
            "text": "So what were you trying to do?",
            "next": "plan"
          }
        ]
      },
      {
        "id": "plan",
        "text": [
          "I needed the fragments to complete the sealing ritual.",
          "But now it may be too late. The power is unstable."
        ],
        "choices": [
          {
            "text": "I'll help you seal it (Mercy)",
            "next": "mercy_choice"
          },
          {
            "text": "You'll face justice for your actions (Justice)",
            "next": "justice_choice"
          }
        ]
      },
      {
        "id": "mercy_choice",
        "text": [
          "Thank you. Together we may be able to complete the ritual.",
          "The corruption can still be contained."
        ],
        "flag": "bram_fate=mercy",
        "next": "conclusion"
      },
      {
        "id": "justice_choice",
        "text": [
          "No! You don't understand what you're doing!",
          "Without the ritual, the artifact will continue to spread corruption!"
        ],
        "flag": "bram_fate=justice",
        "next": "conclusion"
      },
      {
        "id": "conclusion",
        "text": [
          "The decision has been made. The consequences will unfold in time."
        ]
      }
    ]
  }
}
```

## Integration with Existing Systems

The main quest line leverages these existing systems:

1. **DialogUI System** - For all NPC conversations and choice tracking
2. **QuestManager** - For quest state management and progression
3. **NPCManager** - For NPC data and behavior
4. **QuestLog** - For tracking the player's active quests
5. **QuestUI** - For displaying quest information to the player

The main quest chain will be initialized during game startup by loading the main_quests.json file and registering it with the QuestManager.

## Next Implementation Steps

1. Create the JSON files for quest data and dialog scripts
2. Update the NPCs with appropriate dialog_ids and quest_giver flags
3. Implement any special event handlers in game.py for the quest-specific events
4. Create the environment assets for the special locations
5. Design the special monsters for the quest encounters

---

## Notes for Expansion

- Each fork can be further developed with unique dialogue, combat encounters, and moral dilemmas.
- The player's choices here can influence later quests, NPC attitudes, and even the ending of the main story.
- Consider adding reputation systems to track the player's standing with different factions.
- Implement special rewards for different choice paths to encourage replayability.

# Expanded Quest Line: Shadows Over Greymoor

## Step 6: Branch Expansion

### If You Showed Mercy (Bram Survives)

#### Side Quest: Redemption’s Price

- **Objective:** Help Bram atone by dismantling a hidden Order cell in the nearby Whispering Woods.
- **Encounters:**
  - **Ambush:** Order cultists ambush you and Bram, testing your trust in him.
  - **Moral Dilemma:** Bram’s old friend, now a cultist, begs for mercy. Do you spare them or let Bram decide?
- **Resolution:**
  - If you and Bram work together, you uncover a coded message revealing the Order’s next target.
  - If you mistrust Bram or let him handle things alone, he may falter, and the cell escapes, delaying your pursuit of the Order.

#### Town Impact

- **Positive:** Greymoor’s people begin to trust you, and some even offer aid or unique items.
- **Negative:** A few townsfolk remain suspicious of your shadow powers, leading to tense interactions or minor sabotage.

---

### If You Delivered Justice (Bram Dies)

#### Side Quest: Shadows Unleashed

- **Objective:** Contain the spreading shadow corruption in Greymoor.
- **Encounters:**
  - **Shadow Rift:** A rift opens in the town square, spawning shadow creatures.
  - **Rescue Mission:** Save townsfolk trapped by the corruption, but you can’t save everyone.
- **Moral Dilemma:** The artifact’s energy infects a child. Do you risk using your shadowbinding to save them, revealing your powers, or let the town healer attempt a risky cure?
- **Resolution:**
  - If you use your powers, the child survives, but your secret is out—some townsfolk fear you, others are grateful.
  - If you let the healer try, the outcome is uncertain: a successful cure earns trust, but failure leads to grief and blame.

#### Town Impact

- **Positive:** You are respected for your decisive action, and some townsfolk become loyal.
- **Negative:** Fear and suspicion of your powers grow, and the Order’s trail is harder to follow.

---

## Step 7: Future Quest Hooks

### Mercy Path (Bram Ally)

- **Bram’s Redemption Arc:** Bram accompanies you on a future quest, offering unique insights and skills. His fate depends on your continued trust and guidance.
- **Order’s Next Move:** The coded message leads to a new location—perhaps a ruined temple or a city under siege—where the Order is preparing their next ritual.

### Justice Path (Bram Dead)

- **Shadow Stigma:** Rumors of your shadow powers spread, affecting your reputation in other towns and with key NPCs.
- **Order’s Evasion:** The Order, aware of your ruthlessness, sets traps and uses decoys, making your pursuit more dangerous and complex.

---

## Step 8: Long-Term Consequences

- **NPC Relationships:** Allies and potential companions react differently based on your choices in Greymoor. Some may refuse to work with you, while others become more loyal.
- **World State:** Greymoor’s fate (recovered, wary, or damaged) is referenced in later quests, affecting resources, information, and safe havens.
- **Main Story Impact:** The information (or lack thereof) from Greymoor shapes your next major quest, possibly altering the Order’s strength or the difficulty of future encounters.

---

## Example Dialogue Snippets

### Mercy Path

> **Bram:** “You could have ended me, but you didn’t. I won’t waste this chance. Let me help you stop the Order—before more lives are lost.”

### Justice Path

> **Mayor Elira:** “You did what had to be done, but the shadows linger. Some here fear you now. I hope you can prove them wrong.”

---

## Summary Table (Expanded)

| Fork                | Choice         | Immediate Outcome                | Side Quest Unlocked      | Long-term Impact                |
|---------------------|-------------- -|----------------------------------|--------------------------|---------------------------------|
| Who to Trust        | Seren/Bram/Lysa| Different clues, Order secrets   | Varies                   | Sets up confrontation with Bram |
| Justice or Mercy    | Mercy          | Bram becomes ally                | Redemption’s Price       | Informant, compassionate rep, Bram’s arc |
|                     | Justice        | Artifact damaged, chaos spreads  | Shadows Unleashed        | Ruthless rep, Order cautious, shadow stigma |

---

# Quest Line Continuation: The Whispering Temple

## Main Quest: Echoes in the Whispering Temple

### Quest Hook

With Bram’s help, you decipher the coded message found in the Order’s cell. It points to the **Whispering Temple**, an ancient ruin deep in the Mistwood, where the Order is preparing a ritual to corrupt the Heartstone—a magical relic that sustains the region’s life and weather.

---

## Step 1: Journey to the Mistwood

- **Objective:** Travel with Bram to the Mistwood, navigating treacherous terrain and evading Order scouts.
- **Encounters:**
  - **Fae Ambush:** Mischievous fae test your intentions, offering cryptic warnings about the temple’s dangers.
  - **Bram’s Doubt:** Bram confides his guilt and fear, giving you a chance to encourage or challenge him.

---

## Step 2: The Whispering Temple

- **Objective:** Infiltrate the temple, avoid traps, and gather clues about the Order’s ritual.
- **Encounters:**
  - **Shadowbound Guardians:** Animated statues and shadow creatures patrol the halls.
  - **Puzzle Room:** Solve a magical puzzle to access the Heartstone chamber, requiring both your shadowbinding and Bram’s mining knowledge.

---

## Step 3: The Moral Dilemma

Inside the Heartstone chamber, you find the Order’s acolytes performing the ritual. The Heartstone is already partially corrupted, and the ritual’s energy is harming the surrounding forest.

- **Choice:**
  - **A. Disrupt the Ritual Directly:**  
    - Risk unleashing a surge of shadow energy, possibly harming Bram or the forest, but stopping the ritual quickly.
  - **B. Attempt a Cleansing Ritual:**  
    - Use your shadowbinding in a delicate balance with Bram’s knowledge of the Heartstone’s structure. This is slower and riskier—if you fail, the Heartstone may shatter.

---

## Step 4: Consequences

### If You Disrupt the Ritual Directly

- **Outcome:**  
  - The ritual is stopped, but a wave of shadow energy injures Bram and scars the forest. The Heartstone is saved, but the land is tainted.
  - **Bram’s Arc:** Bram is wounded but survives, feeling responsible for the damage. He becomes more determined to make amends.

### If You Attempt the Cleansing Ritual

- **Outcome:**  
  - If successful, the Heartstone is purified, the forest is saved, and Bram’s faith in redemption is strengthened.
  - If you fail, the Heartstone shatters, causing a magical storm and forcing you to flee. The region suffers, and Bram’s guilt deepens.

---

## Step 5: New Side Quests and World Impact

- **Side Quest Unlocked:** “Forest’s Lament”  
  - Help the fae heal the tainted land or deal with the consequences of the magical storm.
- **Bram’s Development:**  
  - If Bram is wounded, you can seek rare herbs or magical aid to heal him, deepening your bond.
  - If Bram’s faith is restored, he becomes a more confident and resourceful ally, unlocking new abilities or information.

- **World State:**  
  - The fate of the Mistwood and its people changes based on your actions—lush and grateful, or scarred and wary.

---

## Example Dialogue

> **Bram (if wounded):** “I thought I could fix what I’d done, but maybe some things can’t be undone. Still, I’ll follow you—if you’ll have me.”
>
> **Fae Elder (if Heartstone is saved):** “You have balanced shadow and light, mortal. The forest remembers kindness—and so do we.”

---

## Future Hooks

- The Order’s next target is revealed: a city where the Veilmaster is gathering power for the final phase of the Eclipse Rite.
- The fae or forest spirits may become allies or adversaries, depending on your choices.
- Bram’s arc continues, with his fate and loyalty shaped by your actions and guidance.

---

## Summary Table

| Choice                    | Immediate Outcome                | Side Quest Unlocked      | Long-term Impact                |
|---------------------------|----------------------------------|--------------------------|---------------------------------|
| Disrupt Ritual Directly   | Ritual stopped, forest scarred, Bram wounded | Forest’s Lament         | Tainted land, Bram’s guilt      |
| Cleansing Ritual (Success)| Heartstone purified, forest saved, Bram redeemed | Forest’s Lament         | Grateful fae, Bram’s growth     |
| Cleansing Ritual (Fail)   | Heartstone shatters, magical storm | Forest’s Lament         | Region suffers, Bram’s guilt    |

---

# Main Questline: The Eclipse Rite

## Act 1: The Awakening
### Key Quest: **Shadows Over Greymoor**  
*(As previously developed)*  
**Outcome:** Player’s early choices define their reputation, allies, and the Order’s responsiveness.

---

## Act 2: The Leyline Crisis
### Key Quest: **City of Luminara**  

**Quest Hook:**  
The Order targets Luminara, a city built atop a nexus of leylines. Corrupting it would accelerate the Eclipse Rite, destabilizing Eldoria’s magic.

---

### Part 1: Infiltration  
**Objective:** Enter Luminara, which is under lockdown due to Order infiltrators.  
- **Paths:**  
  - **Mercy Path (Bram Alive):** Use Bram’s knowledge of mining tunnels to sneak in.  
  - **Justice Path (Bram Dead):** Fight through Order patrols or bribe guards (risking suspicion).  

**Encounter:**  
- **Shadowbound Assassin:** A cloaked figure ambushes you, wielding corrupted leylines. Defeat or subdue them.  
  - **Choice:** Kill them (gains Order intel) or spare them (reveals they’re a mind-controlled citizen).  

---

### Part 2: The Leyline Chamber  
**Objective:** Reach the central leyline chamber beneath the city.  
- **Obstacles:**  
  - **Puzzle:** Use Shadowbinding to manipulate light/darkness to unlock seals.  
  - **Moral Dilemma:** The chamber’s guardian, a celestial spirit, is infected by shadow.  
    - **Option 1:** Purify it (requires sacrificing a rare relic).  
    - **Option 2:** Destroy it (releases energy, damaging the city but halting corruption).  

**Outcome:**  
- **Purify:** The spirit becomes an ally, aiding in future quests.  
- **Destroy:** Leyline surges cause earthquakes—Luminara’s districts begin to collapse.  

---

### Part 3: The Order’s Gambit  
**Objective:** Stop the Order’s ritual in the leyline chamber.  
- **Fork:**  
  - **Mercy Path:** Bram distracts the cultists while you confront the Order’s High Priestess.  
  - **Justice Path:** You face the Priestess alone, but she’s prepared for your ruthless tactics.  

**Climactic Choice:**  
The Priestess offers a deal: spare her, and she’ll reveal the Veilmaster’s location.  
- **Accept:** She escapes, but you gain critical intel. The city views you as pragmatic.  
- **Refuse:** Kill her, but the Veilmaster’s plans remain shrouded. The city hails you as a hero.  

**Consequences:**  
- Luminara’s survival (and attitude toward you) depends on earlier choices.  
- The Veilmaster’s next move is revealed: a fortress in the Shattered Peaks.  

---

## Act 3: The Shattered Peaks  
### Key Quest: **The Veilmaster’s Fortress**  

**Quest Hook:**  
The Order’s stronghold is hidden in a mountain range torn apart by unstable magic. The Eclipse Rite is nearing completion.  

---

### Part 1: Ascending the Peaks  
**Objective:** Navigate the treacherous terrain.  
- **Paths:**  
  - **Stealth:** Use Shadowbinding to cloak through Order patrols.  
  - **Force:** Fight through mutated beasts and cultists.  
  - **Alliance:** If you spared the Priestess, she guides you (but may betray you).  

**Encounter:**  
- **The Forgotten Titan:** A gargantuan golem, half-consumed by shadow, blocks your path.  
  - **Option 1:** Repair its core (requires rare materials).  
  - **Option 2:** Destroy it (triggers avalanches, altering the map).  

---

### Part 2: The Heart of the Eclipse  
**Objective:** Confront the Veilmaster in the ritual chamber.  

**Revelation:**  
- The Veilmaster is your ancestor, bound to the Eclipse Rite by a millennia-old pact. Your Shadowbinding is a shard of his power.  
- **Choice:** Join him to reshape the world, or defy him and break the cycle.  

**Final Battle:**  
- Phase 1: Fight the Veilmaster’s physical form.  
- Phase 2: Enter the Shadow Realm, where your choices throughout the game empower or weaken you.  

---

### Part 3: The Eclipse Rite’s End  
**Endgame Choices:**  
1. **Embrace the Shadow:** Merge with the Veilmaster, becoming a godlike entity. Eldoria is reborn in darkness, with you as its ruler.  
2. **Destroy the Rite:** Shatter the ritual, sacrificing your life. Eldoria survives, but magic fades, and the world enters an age of uncertainty.  
3. **Forge a New Path:** Use your Shadowbinding to absorb and redistribute the Eclipse energy, balancing light and dark. Eldoria is transformed, and you become a wandering guardian.  

**Epilogue:**  
- NPCs and locations react to your choice, with unique endings for allies, towns, and factions.  

---

## Branching Summary Table

| Act | Key Decision                | Mercy Path Consequence       | Justice Path Consequence      |
|-----|----------------------------|-------------------------------|--------------------------------|
| 1   | Sparing Bram               | Informant, compassionate rep  | N/A (Bram dead)               |
| 2   | Leyline guardian choice    | Celestial ally or city damage | Same, but harder diplomacy    |
| 3   | Veilmaster’s offer         | Join, defy, or balance        | Join, defy, or balance        |

---

