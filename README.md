# FRESH: Flight Rule Evaluation Script Helper

![Project logo](https://github.jpl.nasa.gov/teamtools-studio/teamtools-documentation/blob/main/docs/images/tts_image_artifacts/fresh.png)

## About Teamtools Studio

Teamtools Studio Utilities is part of JPL's Teamtools Studio (TTS).

TTS is an effort originated in JPL's Planning and Execution section to centralize shared repositories across missions. This benefits JPL by reducing cost through reducing duplicated code, collaborating across missions, and unifying standards for development and design across JPL.

Although Planning and Execution is primarily concerned with flight operations, the TTS suite has been generalized and atomized to the point where many of these tools are applicable during other mission phases and even in non-spaceflight contexts. Through our work flying space missions, we hope to provide tools to the open source community that have utility in data analysis or planning for any complex system where failure is not an option.

For more infomation on how to contribute, and how these libraries form a complete ecosystem for high reliability data analysis, see the [Full TTS Documentation](https://github.jpl.nasa.gov/pages/teamtools-studio/teamtools_documentation/).

## What is FRESH?

### Overview

FRESH is a static Flight Rule checker. At JPL Flight Rules typically represent:

* Residual issues found in development but not fully fixed prior to flight
* Other known ways we do not wish to operate our spacecraft. 
* Idiosyncracies and "Use as is" issues disconvered in the design

Flight rule may be used to safeguard against misconfiguration, to keep us from entering a failure mode discovered in testing, or even just to make sure operations remain efficient and operators stay sane.

A given mission can have between hundreds and thousands of Flight Rules, making manaully checking them all but impossible in the time operators are given to plan a spacecraft command load. While some Flight Rules can be highly complex and need bespoke code, many can be at least partially checked with simple constructs. FRESH is meant to be a static checker that checks spacecraft commands sequences in the way an IDE would check linting rules, and it is optimized to check these simple rule architypes while also defining an interface to define more complex rules if needed.

### Rule Architypes

Nearly every Flight Rule can at least be partially checked with one of a few architypes

* Do not send command X in condition Y
* Do not send command X with arguments Y in condition Z
* Do not send command X within Y seconds before/after Command Z in condition W

In all cases, the command and argument portions of these architypes are actually fairly straightforward for a computer to check, but can be very taxing for a human. On the other hand, the more open ended the "condition Y" is, the more difficult it is to implement in a way where a computer can check it, with implementation complexity exploding around rare corner cases. However, more often than not, the humans in the loop of spacraft planning can quickly disposition these conditions by simply leveraging their situational awareness (are we in safe mode? Did that werid thing that almost never happens happen today?).

In this way, a strong FRESH implementation serves as a filter. Thousands of Flight Rules get checked, and out comes a decimated list of rules that still need human intervention, often on the order of 20-50, which is a much more tractable number for a human to check on a tactical timeline (e.g. if command X is nowhere in today's command load, no one needs to check if we are in condition Y, so FRESH can disposition the rule without a human's help).

### A note on command timing rules
FRESH does not simulate sequences. To the extent that it can handle timing conditions, it can only see the time stamps one sequence at a time as it is designed to be a static checker. 

For spacecraft that use parallel sequences or do not explicitly and statically include their command timing in their sequences, some of the above architypes should be used with care or not used at all. 

Any project's Flight Rule implementation will still only be as good as the team is able to judiciously write, edit, and implement their rules. FRESH can be a very strong part of that solution, but it requires a lot of human intuition. Like most TTS tools, FRESH is intended to get the nit-picky programming challenges out of the way so a human can get to apply that intuition more simply and  without distraction by unrelated technical issues.

If a project need to check rules on more complex timing, see our digital twin library [tts_seq](https://nasa-jpl-teamtools-studio.github.io/teamtools_documentation/repositories/tts_seq/).

### Projects Currently Supported

* Mars 2020 (Prototype only)
* Europa Clipper
* NISAR
* DemoSat