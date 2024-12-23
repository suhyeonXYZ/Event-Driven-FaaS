# 분산 Edge Cloud 환경에서 <br/>Event 기반 Function-as-a-Service 기능 개발<br/>[![license](https://img.shields.io/github/license/dohyunKim12/FaaS-Soong.svg?style=flat-square)](https://github.com/dohyunKim12/FaaS-Soong/blob/master/LICENSE)

> :trophy: 2021년 **NET CHALLENGE CAMP SEASON8 GOLD AWARD**. 숭실대학교 팀 빠숭(FaaSoong)<br/> 
> https://www.koren.kr/lib/Common/Com/ComDownload.asp?ttp=cny1&tno=58 
> https://www.youtube.com/watch?v=UieUycoFO5o <br/> 
> https://youtu.be/4P43L8422RM?t=199

## Summary

대용량 네트워크 KOREN(KoreaAdvancedResearchNetwork) 에서 쿠버네티스로 클러스터를 구성하고 함수형 서비스를 배포하는 서버리스 모델 운영.

KEDA(Kubernetes-Event-Driven-AutoScaling)을 활용한 Scale-to-Zero 구현.

평상시에 동작하지 않는 상태에서 이벤트 발생 기반으로 서비스 생성 및 Scale-Out 하는 Serverless Computing Model을 구현한다. Edge-Cloud 환경에서 Event 기반으로 동작하는 응용 예로서 특정 상황 발생 시(예: 교통사고 발생 등) CCTV가 복잡한 인식기능을 하는 외부 OpenService를 이용하여 해당 사건을 처리하는 여러 서비스를 필요한 곳에 제공하는 FaaS(Function as a Service) Model을 구현한다.

## Developers

**숭실대학교 전자정보공학부**

-   김도현(Dohyun Kim)
-   윤창섭(Changseop Yoon)
-   송수현(Suhyun Song)
-   송지원(Jiwon Song)

## About KOREN
KOREN은 전국 10개 지역노드(서울, 판교, 수원, 대전, 광주, 대구, 부산, 춘천, 전주, 제주)간 10Gbps ~ 360Gbps로 연결되어 구축·운용
홍콩 및 싱가폴 해외 노드를 통해 TEIN* 및 아시아, 유럽, 미국의 각 연구망들과 100Gbps로 연결되어 구축·운용


## Scope

**Point of Infrasturcture**

-   Kubernetes를 활용한 Cluster 구축.
-   Cluster Monitoring을 위해 Prometheus와 Grafana를 설치.
-   KEDA 및 RabbitMQ Server 설치.

**Point of Service**

-   사고 상황을 감지하는 Deep Learning Model을 FaaS로써 배포.
-   상황 감지를 단계적으로 구현함으로써 자원 효율성을 극대화.
-   OpenCV를 이용하여 움직임을 감지하는 애플리케이션을 워커 노드에서 동작.
-   이벤트 기반의 함수형 서비스 제공.

## Scenario

~~~
1. 워커 노드에서 CCTV 영상을 수신하면서 움직임 감지 Pod 항시 동작
2. 움직임 감지 후 RabbitMQ의 Motion 큐에 메시지 전송
3. KEDA가 RabbitMQ 메시지를 받아 HPC에 세부 상황 감지 Pod 배포
4. 세부 상황 감지 후 RabbitMQ의 해당 큐에 메시지 전송
5. 사고 데이터를 DB에 저장 후 실시간 위험 상황 알림 서비스 배포
6. 서비스 종료 후 포드 소멸
~~~


## GPU Resource Monitoring

함수형 서비스(FaaS) 구현에 따른 GPU Resource 사용률 측정.
GPU를 사용하는 Pod가 특정 이벤트 기반으로 동작함을 확인.

