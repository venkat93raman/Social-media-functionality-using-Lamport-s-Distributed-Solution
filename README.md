# Social-media-functionality-using-Lamport-s-Distributed-Solution
The goal of the project was to implement a distributed system to simulate the social media 'Like' functionality. Distributed environment consisted of 5 systems with support for real-time addition for new systems. Communication between the systems was established using socket communication(TCP/IP protocol) written in Python language.  The distributed system was designed to handle social media read and like functionality where each client can read or like the post and keep track of the likes for the post. The mutual exclusion problem for keeping the track of number of likes was solved using Lamport’s distributed algorithm.