"""pytest配置"""
import pytest
from doc_router import DocumentRouter


@pytest.fixture
def router():
    """创建DocumentRouter实例"""
    return DocumentRouter(chunk_size=500, chunk_overlap=100)


@pytest.fixture
def sample_guide_text():
    """指南类文档示例"""
    return """第一章 总则

第一条 为了规范医疗行为，保障医疗安全，根据《中华人民共和国执业医师法》等有关法律、法规，制定本规范。

第二条 本规范适用于医疗机构及其医务人员在诊疗活动中的行为。

第二章 诊断

第三条 医师应当询问病史，进行体格检查，并根据需要进行辅助检查。

第四条 医师应当根据患者的症状、体征和检查结果，作出初步诊断。

第三章 治疗

第五条 医师应当根据诊断结果制定治疗方案。

第六条 治疗方案应当符合诊疗规范。

第四章 护理

第七条 护士应当执行医嘱，观察患者病情变化。

第八条 护理记录应当及时、准确、完整。

第五章 康复

第九条 康复治疗应当在医师指导下进行。

第十条 康复方案应当个体化制定。

本操作指南旨在为临床实践提供参考。"""


@pytest.fixture
def sample_dictionary_text():
    """词汇表文档示例"""
    return """
词汇表

高血压（hypertension）：指动脉血压持续升高，收缩压≥140mmHg和/或舒张压≥90mmHg。

糖尿病（diabetes mellitus）：一组以高血糖为特征的代谢性疾病。

冠心病（coronary heart disease）：冠状动脉粥样硬化性心脏病的简称。

心肌梗死（myocardial infarction）：冠状动脉急性闭塞导致的心肌缺血性坏死。
"""


@pytest.fixture
def sample_paper_text():
    """学术论文示例"""
    return """
# 摘要

目的：探讨高血压患者血压控制与心血管事件的关系。

方法：选取2020年1月至2023年12月在我院就诊的高血压患者500例，随访2年。

结果：血压控制良好组心血管事件发生率显著低于对照组（P<0.05）。

结论：良好的血压控制可显著降低高血压患者心血管事件风险。

## 关键词

高血压；血压控制；心血管事件

## 参考文献

[1] 张三, 李四. 高血压治疗研究进展[J]. 中华心血管病杂志, 2023, 51(1): 1-5.
[2] Wang L, Zhang Y. Blood pressure control and cardiovascular outcomes[J]. JAMA, 2022, 328(12): 1234-1240.
"""


@pytest.fixture
def sample_textbook_text():
    """教科书示例"""
    return """
第一章 内科学基础

第一节 呼吸系统

呼吸系统由呼吸道和肺组成。呼吸道包括鼻、咽、喉、气管和支气管。

肺是进行气体交换的器官，位于胸腔内，左右各一。

第二节 循环系统

循环系统由心脏和血管组成。心脏是血液循环的动力器官。

血管分为动脉、静脉和毛细血管三类。

第二章 常见疾病

第一节 上呼吸道感染

上呼吸道感染是鼻腔、咽或喉部急性炎症的总称。

主要症状包括：发热、头痛、乏力、咳嗽、流涕等。
"""