#!/usr/bin/env bash
set -euo pipefail
cat > story.txt <<'STORY_EOF'
The Lighthouse Keeper's Daughter

Ines climbed the stairs of the lighthouse every night at nine. She counted them as she went, one hundred and twelve, and she never lost count, not once in eleven years.

Tonight she saw that the lamp room door was open. She felt a cold draft come down the stairwell and she felt her heart beat faster. Her father always shut that door. He shut it the way he shut everything, carefully and completely and with a small nod, as if the door had agreed to something.

"Papa?" she called up quietly. Nobody answered. The wind answered, the way it always did, with nothing useful to say.

At the top she found the lamp burning and the logbook open on the desk. The last entry was in her father's hand, dated tomorrow. Ines read it twice. Ships sighted: none. Weather: clearing. Keeper: absent.

Down below, on the rocks, Tomas was waiting for her. He knew what the entry meant before she did. He had always known teh things about the light that nobody told him.

She closed the logbook and sat down in her father's chair, and for the first time in eleven years she did not count anything at all.
STORY_EOF
printf '{"works": "editwright-works"}\n' > .editwright.json
