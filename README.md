Simbl is a very simple language for expressing directed graphs whose nodes can have children, and nodes and edges can have annotations. There are three keywords: ANNO (annotation), CALLS, CALLEDBY (alias CBY). The following example shows every feature in Simbl.

```
My_Computer
	Browser
		CALLS Operating_System ANNO invokes OS's networking capabilities to connect to github.com
	Operating_System

DNS_Server
	CBY Operating_System ANNO DNS server returns IP address of github.com

Git_Server ANNO serves the webpages, stores github data, etc
	CALLEDBY Browser
```

gv.py transpiles Simbl to Dot, a much more powerful graph language, for which visualization engines exist. The above Simbl turns into the following Dot:

```
digraph G {
    compound=true;
    fontname="Helvetica" fontsize=8;
    
    node [
        shape=box color=steelblue
        fontname="Helvetica" fontsize=8 
        margin=0.03 width=0 height=0];
    edge [
        fontname="Helvetica" fontsize=6 fontcolor=steelblue
        color=steelblue
        arrowsize = 0.5]

        subgraph cluster_0 {
                label ="My_Computer"
                Browser;
                Operating_System;
        }
        DNS_Server;
                Git_Server[label=<Git_Server<BR /><FONT POINT-SIZE='6'>serves the webpages, stores github data, \netc </FONT>>];

	Browser->Operating_System[label="invokes OS's networking capabilities \nto connect to github.com " fontcolor="0.57 0.25 0.8" color="0.57 0.25 0.8"];
	Operating_System->DNS_Server[label="DNS server returns IP address of github.com \n" fontcolor="0.74 0.25 0.8" color="0.74 0.25 0.8"];
	Browser->Git_Server[];
}
```

Which GraphViz will render as
![image](https://user-images.githubusercontent.com/32442230/98658815-52201480-22f8-11eb-83f5-4c313c3f91d2.png)

Rules:
1. Use tabs to 
2. CALLS or CBY  is always on the line after the name of the source node. ANNO is always on the same line as the node or edge it modifies.


:::

next steps
https://github.com/dreampuf/GraphvizOnline