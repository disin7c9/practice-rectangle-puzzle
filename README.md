# practice-rectangle-puzzle
split an image and concatenate them


## 사용법
tasks/argument.py 에서 config 설정 후 main directory에서 
>>>python cut.py
>>>python merge.py

## cut.py
이 문제에 한해서 2x2, 3x3보다 일반화가 생각하기 편해서 MxN split을 구현하였다.
이미지에 대한 형상 변환과 차원 축 변경을 통하여 이를 잘라냈다.
(해당 방법에 대한 출처: https://stackoverflow.com/questions/42297115)

## merge.py
sub image들에 대하여 같은 형태를 가진 횡적 나열들을 만든 다음 이를 종적으로 이어붙이는 방법을 사용하였다.
horizontal 및 vertical concatenation 시에 각각 좌우, 상하 방향으로 1 pixel 너비의 edge간의 더 낮은 거리 점수를 가진 하위 이미지 (flip, rot의 형상 변환도 고려함) 를 전체에서 선택한다.
다만 edge간의 유사도 측정에 대하여 순진하게 판단하여 평균 L1 거리나 Pearson correlation, cosine similarity 등으로 문제를 해결할 수 있을 것이라 알고리즘 구상 단계에서 착각하였고, 그 결과 이미지 재구성은 가능하였으나 하위 이미지 순서 재정렬은 실패하였다.
