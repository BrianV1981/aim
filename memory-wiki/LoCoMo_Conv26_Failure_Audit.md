# LoCoMo Conv-26 Baseline Failure Audit

**Total Questions:** 199
**Total Exact Match Failures:** 60

## Category 1: Genuine Reasoning Failures & Human Annotation Errors
Count: 5
These are questions where the A.I.M. agent provided a coherent answer that mathematically failed the Exact Match string comparison against the Ground Truth.

**1. Q:** When did Caroline and Melanie go to a pride fesetival together?
- **PREDICTED:** The Sunday before 19 August 2023_
- **GROUND TRUTH:** 2022

**2. Q:** [V2_REPLACEMENT] Based on Maria's message, when did she learn about the importance of self-care the "hard way"?
- **PREDICTED:** 2022
- **GROUND TRUTH:** Last year

**3. Q:** Would Melanie go on another roadtrip soon?
- **PREDICTED:** Likely no, as the recent one was traumatic.
- **GROUND TRUTH:** Uncertain; although the trip started badly with the accident, the family continued and enjoyed the Grand Canyon, suggesting Melanie values family trips

**4. Q:** What precautionary sign did Caroline see at the café?
- **PREDICTED:** A sign stating that someone is not able to leave.
- **GROUND TRUTH:** A sign stating that someone is not being able to leave

**5. Q:** What does Caroline love most about camping with her family?
- **PREDICTED:** Being present and bonding with her family_
- **GROUND TRUTH:** Being present and bonding with her family

## Category 2: Token Fragmentation (The `_制` Hallucination)
Count: 42
These failures occurred in the later half of the 199-question continuous session. The massive context window bloated the LLM's attention mechanism, causing it to append a hallucinated Chinese character (`_制`) to otherwise correct answers.

**1. Q:** What creative project do Mel and her kids do together besides pottery?
- **PREDICTED:** Painting_制
- **GROUND TRUTH:** painting

**2. Q:** What did Caroline realize after her charity race?
- **PREDICTED:** Self-care is important_制
- **GROUND TRUTH:** self-care is important

**3. Q:** What are Melanie's plans for the summer with respect to adoption?
- **PREDICTED:** Researching adoption agencies_制
- **GROUND TRUTH:** researching adoption agencies

**4. Q:** Why did Melanie choose the adoption agency?
- **PREDICTED:** Inclusivity and support for LGBTQ+ individuals_制
- **GROUND TRUTH:** because of their inclusivity and support for LGBTQ+ individuals

**5. Q:** What is Melanie excited about in her adoption process?
- **PREDICTED:** Creating a family for kids who need one_制
- **GROUND TRUTH:** creating a family for kids who need one

**6. Q:** What does Melanie's necklace symbolize?
- **PREDICTED:** Love, faith, and strength_制
- **GROUND TRUTH:** love, faith, and strength

**7. Q:** What country is Melanie's grandma from?
- **PREDICTED:** Sweden_制
- **GROUND TRUTH:** Sweden

**8. Q:** What was grandma's gift to Melanie?
- **PREDICTED:** Necklace_制
- **GROUND TRUTH:** necklace

**9. Q:** What was grandpa's gift to Caroline?
- **PREDICTED:** Necklace_制
- **GROUND TRUTH:** necklace

**10. Q:** What is Caroline's hand-painted bowl a reminder of?
- **PREDICTED:** Art and self-expression_制
- **GROUND TRUTH:** art and self-expression

**11. Q:** What did Caroline and her family do while camping?
- **PREDICTED:** Explored nature, roasted marshmallows, and hiked_制
- **GROUND TRUTH:** explored nature, roasted marshmallows, and went on a hike

**12. Q:** What kind of counseling workshop did Melanie attend recently?
- **PREDICTED:** LGBTQ+ counseling workshop_制
- **GROUND TRUTH:** LGBTQ+ counseling workshop

**13. Q:** What motivated Melanie to pursue counseling?
- **PREDICTED:** Her personal journey and the support she received_制
- **GROUND TRUTH:** her own journey and the support she received, and how counseling improved her life

**14. Q:** What kind of place does Melanie want to create for people?
- **PREDICTED:** A safe and inviting place for growth_制
- **GROUND TRUTH:** a safe and inviting place for people to grow

**15. Q:** Did Caroline make the black and white bowl in the photo?
- **PREDICTED:** No_制
- **GROUND TRUTH:** No

**16. Q:** What are the new shoes that Caroline got used for?
- **PREDICTED:** Running_制
- **GROUND TRUTH:** Running

**17. Q:** What is Caroline's reason for getting into running?
- **PREDICTED:** To de-stress and clear her mind_制
- **GROUND TRUTH:** To de-stress and clear her mind

**18. Q:** What does Caroline say running has been great for?
- **PREDICTED:** Her mental health_制
- **GROUND TRUTH:** Her mental health

**19. Q:** What did Melanie see at the council meeting for adoption?
- **PREDICTED:** Many people wanting to create loving homes for kids in need_制
- **GROUND TRUTH:** many people wanting to create loving homes for children in need

**20. Q:** What inspired Melanie's painting for the art show?
- **PREDICTED:** Visiting an LGBTQ center and capturing unity and strength_制
- **GROUND TRUTH:** visiting an LGBTQ center and wanting to capture unity and strength

**21. Q:** What inspired Caroline's sculpture for the art show?
- **PREDICTED:** Visiting an LGBTQ center and capturing unity and strength_制
- **GROUND TRUTH:** visiting an LGBTQ center and wanting to capture unity and strength

**22. Q:** How often does Caroline go to the beach with her kids?
- **PREDICTED:** Once or twice a year_制
- **GROUND TRUTH:** once or twice a year

**23. Q:** How did Caroline feel while watching the meteor shower?
- **PREDICTED:** In awe of the universe_制
- **GROUND TRUTH:** in awe of the universe

**24. Q:** Is Oscar Melanie's pet?
- **PREDICTED:** No_制
- **GROUND TRUTH:** No

**25. Q:** Where did Oscar hide his bone once?
- **PREDICTED:** In Melanie's slipper_制
- **GROUND TRUTH:** In Melanie's slipper

**26. Q:** What activity did Melanie used to do with her dad?
- **PREDICTED:** Horseback riding_制
- **GROUND TRUTH:** Horseback riding

**27. Q:** What did Melanie make for a local church?
- **PREDICTED:** A stained glass window_制
- **GROUND TRUTH:** a stained glass window

**28. Q:** What did Melanie find in her neighborhood during her walk?
- **PREDICTED:** A rainbow sidewalk_制
- **GROUND TRUTH:** a rainbow sidewalk

**29. Q:** Which song motivates Melanie to be courageous?
- **PREDICTED:** Brave by Sara Bareilles_制
- **GROUND TRUTH:** Brave by Sara Bareilles

**30. Q:** What type of instrument does Caroline play?
- **PREDICTED:** Clarinet and violin_制
- **GROUND TRUTH:** clarinet and violin

**31. Q:** Which classical musicians does Caroline enjoy listening to?
- **PREDICTED:** Bach and Mozart_制
- **GROUND TRUTH:** Bach and Mozart

**32. Q:** Who is Caroline a fan of in terms of modern music?
- **PREDICTED:** Ed Sheeran_制
- **GROUND TRUTH:** Ed Sheeran

**33. Q:** What setback did Caroline face recently?
- **PREDICTED:** Injury forcing a break from pottery_制
- **GROUND TRUTH:** She got hurt and had to take a break from pottery.

**34. Q:** What does Caroline do to keep herself busy during her pottery break?
- **PREDICTED:** Read a book and paint_制
- **GROUND TRUTH:** Read a book and paint.

**35. Q:** What was the poetry reading that Melanie attended about?
- **PREDICTED:** Transgender people sharing their stories_制
- **GROUND TRUTH:** It was a transgender poetry reading where transgender people shared their stories.

**36. Q:** What happened to Caroline's son on their road trip?
- **PREDICTED:** He got into an accident_制
- **GROUND TRUTH:** He got into an accident

**37. Q:** How did Caroline's son handle the accident?
- **PREDICTED:** He was scared but reassured_制
- **GROUND TRUTH:** He was scared but reassured by his family

**38. Q:** How did Caroline feel about her family after the accident?
- **PREDICTED:** They are important and mean the world to her_制
- **GROUND TRUTH:** They are important and mean the world to her

**39. Q:** How did Caroline's children handle the accident?
- **PREDICTED:** They were scared but resilient_制
- **GROUND TRUTH:** They were scared but resilient

**40. Q:** How did Caroline feel after the accident?
- **PREDICTED:** Grateful and thankful for her family_制
- **GROUND TRUTH:** Grateful and thankful for her family

**41. Q:** What was Caroline's reaction to her children enjoying the Grand Canyon?
- **PREDICTED:** Happy and thankful_制
- **GROUND TRUTH:** She was happy and thankful

**42. Q:** What did Caroline do after the road trip to relax?
- **PREDICTED:** Went on a nature walk or hike_制
- **GROUND TRUTH:** Went on a nature walk or hike

## Category 3: Parsing Errors (Log Truncation)
Count: 13
These questions were successfully answered by the agent in the terminal, but the tmux screen-wrap chopped the string in half, causing the Python recovery script to miss them.

**1. Q:** [V2_REPLACEMENT] What is the Guinea pig in the image doing as it peers out of the wooden tunnel?

**2. Q:** [V2_REPLACEMENT] Which band's name is visible in the lower left corner of the concert photo?

**3. Q:** [V2_REPLACEMENT] According to the book cover in the image, who are the authors of "The Kobold Guide to Board Game Design"?

**4. Q:** When did Caroline encounter people on a hike and have a negative experience?

**5. Q:** What type of individuals does the adoption agency Caroline is considering support?

**6. Q:** What kind of counseling and mental health services is Caroline interested in pursuing?

**7. Q:** What did Melanie and her family see during their camping trip last year?

**8. Q:** Why did Melanie choose to use colors and patterns in her pottery project?

**9. Q:** How do Melanie and Caroline describe their journey through life together?

**10. Q:** What type of individuals does the adoption agency Melanie is considering support?

**11. Q:** What kind of counseling and mental health services is Melanie interested in pursuing?

**12. Q:** What did Caroline and her family see during their camping trip last year?

**13. Q:** Why did Caroline choose to use colors and patterns in her pottery project?

