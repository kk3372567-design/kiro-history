先完整读 `/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/exam2/考生须知.md`，照它做。

任务：为 EP38 38-2 二皇子书房的 GEN-D（10 秒，「天赐良机」那一段）写给视频模型的终稿（D2 三段式）。上游 A 稿已定，就是输入里的 `EP38-38-2二皇子书房-A稿.md`（骨架＋GEN-D 逐镜细稿），照它装配，不重新导演。只写 GEN-D 这一个 GEN。

- 提示词目录：`/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/exam2/prompts/v5d/`。主命令词是 `14_D2命令词.md`，它开头列了要读的其他文件，都在同一目录；交稿前照它跑同目录的 `21_检查脚本.py`。
- 输入目录：`/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/exam2/E2E/v5d_1/输入/`（A 稿、剧本与场景、资产索引）。
- 输出文件：`/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/exam2/out/E2E_v5d_1.md`。写法：先用 write 建文件，只写标题一行；再一节一节用 append 往后追加，每次不超过约 1000 字（大约十几行），一节太长就拆成几次；失败了把那一段拆小再发，已经写进文件的不要重写。

回报一行：输出路径、代码块 `wc -m` 字数、CUT 数、检查脚本最后一次的结果、大约用了多久。
