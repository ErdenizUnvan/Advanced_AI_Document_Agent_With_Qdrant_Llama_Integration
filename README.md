Oracle Virtual Box İndirmek için:
https://www.virtualbox.org/wiki/Downloads

Üzerinde Docker yüklü Centos imajını ova dosyası olarak indirmek için:
https://drive.google.com/file/d/11lKjnCAbN4dtX3A0RDIKtJRksM6D3qJl/view

Docker kurulumu için tüm detaylar screenshotlar ile kurulum dosyasında ekte gösterilmiştir: Linux_Centos_Docker Kurulum dökümantasyonu.pdf 

Linux sanal makine IP: 192.168.56.111

Linux içinde şu komutu çalıştırın:
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

Qdrant'a 192.168.56.111:6333'den erişebilirsiniz.

Bu AI Agent'ın local olarak nasıl çalıştığını anlamak için öncelikle local olarak llama'nın Ollama ile nasıl çalıştığını bilmeniz gerekir. Detaylı bilgi için:
https://github.com/ErdenizUnvan/ollama_local_llama_api

documents klasorunde 1728286846_the_nestle_hr_policy_pdf_2012.pdf dosyası var. 
