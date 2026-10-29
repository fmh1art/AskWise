# A2: Ask only questions that change the answer

研究对象：自然语言数据分析中，用户意图与数据修复均有歧义时，选择必要的澄清问题，并说明答案对哪些未确定假设不变。

用户授权：2026-10-29，端到端研究；两个指定 API；在 projects 下建立代码及 ACL LaTeX 仓库；可向 AutoResearchSkills 总结通用经验。用户已明确确认 ACL 主会质量、API 无总费用上限、每轮实验尽量一天内完成。

代码：`/home/fanmeihao/projects/A2-research`。论文：`/home/fanmeihao/projects/A2-paper`。大文件：`/data01/fanmeihao-data/A2-research`。

关键区别尚待证明：AIR 已按当前数据库的执行结果剪枝意图，EC2 已解决有限假设的等价类辨识。我们不能把这两项当新方法。候选研究重点是修复不确定性下的过早剪枝、组合交互和候选集合不完整时的停止错误。

验收：可复跑代码、真实模型调用及 usage、强基线和消融、独立测试、误差与不确定性、官方 ACL 模板可编译论文。建仓、合成结果或草稿均不代表达到投稿质量。

未知项：真实任务上联合歧义的普遍性；完整候选集合假设的可行性；超越 EC2/最优小规模决策树的实际贡献。
