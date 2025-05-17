# AI Code Generator

This project is an AI-assisted code generation application that uses Llama to generate Python code based on user prompts.
It is done as a test of my internship application into S4E.

## Deneyimim

Bu kısımda, görevin ikinci aşamasını nasıl yaptığım ve yaşadığım sorunlar hakkında bilgi vereceğim.

### kubeadm IP Sorunu ve Nasıl Başa Çıktığım: 
Bu görevde, birçok farklı uygulamayı deneyimleme fırsatım oldu. 

Bir sanal makineyi oluşturma ve içerisine Ubuntu kurma kısmını rahat ve doğru bir şekilde yapana kadar Hyper-V, VirtualBox, Ubuntu Multipass, VMware Workstation, Vagrant gibi birçok yazılımı denedim. 

Sanal makine kurma, farklı sanal makinelerin kendi aralarında bağlantılarını sağlama, sanal makinelerin dış dünya sayılan internete bağlantısını sağlama konusunda birçok kez kurulum yaptım. 
Bunların sonucunda NAT ve Host-Only Network kullanımlarını en rahat ve doğru şekilde VirtualBox ve Vagrant ikilisini kullanarak yapabildiğime karar verdim.

Vagrantfile yazımını, Vagrantfile'ın nasıl çalıştığını ve "vagrant init", "vagrant up", "vagrant destroy -f", "vagrant ssh <node-name>" gibi komutların nasıl kullanıldığını öğrendim.

!!! Burada bilmediğim kısım şuydu, hem NAT hem de Host-Only bağlantının kurulduğu çok node'lu Kubernetes Cluster kurulumunda, master node içerisindeyken:

   "sudo kubeadm init --pod-network-cidr=10.10.0.0/16" 
komutu yerine
   "sudo kubeadm init --apiserver-advertise-address=192.168.100.1 --pod-network-cidr=10.10.0.0/16"
komutunu kullanmam gerekiyordu.

"API server advertise address" bilgisi kurulumda açıkça tanımlanmazsa; kubeadm default olarak sistemdeki ilk geçerli non-loopback IP adresini otomatik olarak seçiyormuş. 

![image](https://github.com/user-attachments/assets/852f1554-5c0d-4ff6-b880-6739c900baa8)

Benim sistemimde adresler, fotoğrafta verdiğim gibi

"lo (127.0.0.1) → geçersiz", "enp0s3 → IP: 10.0.2.15" (ilk geçerli adres), "enp0s8 → IP: 192.168.56.10"

şeklinde olduğu için; Internal IP olan Host-Only bağlantısının sağladığı IP'yi (master node için 192.168.56.10) değil, External IP olan NAT bağlantısının sağladığı IP'yi (10.0.2.15) seçiyormuş.

Ben bunun bilgisine önceden sahip olmadığım için,

   "sudo kubeadm join --v=5 192.168.56.10:6443 --token hsb19j.7rm5z71s606ro1jk
   --discovery-token-ca-cert-hash sha256:c40ef1dd0129164633cadd2643e67b10abe88e86444f35964f14b17c
   9837e549"

komutunu çalıştırdığımda 

"[preflight] Running pre-flight checks
error execution phase preflight: couldn't validate the identity of the API Server: failed to request the cluster-info ConfigMap: Get "https://10.0.2.15:6443/api/v1/namespaces/kube-public/configmaps/cluster-info?timeout=10s": dial tcp 10.0.2.15:6443: connect: connection refused"

şeklinde hata alıyordum.

"ping -3 c google.com", "ping 8.8.8.8", "ping 10.0.2.15", "telnet 10.0.2.15 6443", "nc -zv 10.0.2.15 6443"

komutlarıyla ağ yapılandırmasının neresinde sorun olduğunu anlamaya çalıştım. ping komutlarının bir kısmı çalışmasına rağmen curl komutlarına geçtiğimde veya doğru bağlantıyı gerektiren kubeadm join komutunu denediğimde yine sorun çıkıyordu. 

Bu durumdan kaynaklanan tüm sorunları anlayabilmek ve çözebilmek için sıklıkla "curl -k https://192.168.56.10:6443", "ifconfig", "ip a", "kubectl config view", "sudo netstat -tulpn | grep 6443", "sudo kubeadm reset", "sudo systemctl restart containerd.service", "sudo systemctl restart kubelet.service", "sudo systemctl enable kubelet.service" gibi komutlar kullanarak sorunu atlatmaya çalıştım.

Sorunu anladığımda, çok fazla dosyayı değiştirmiş olduğum için yeniden başlamanın karışıklık ihtimalini azaltarak daha doğru olabileceğine karar verdim. Belki de bu hafta elli kere olduğu gibi, yeniden sanal makineleri kurdum. Temiz bir başlangıç gibisi yok. Fakat maalesef projenin böyle bir aksaklık günlerime mal oldu. 

### CNI (pod network) Eklentisi Seçimi, Kurulumu ve Kullanımı

Podların etkileşimlerini kısıtlama konusunda control-plane kurulumuyla beraber gelen mesajın içindeki opsiyonlara bağlıydı.

"You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/"
 
Flannel’in default kurulumu bu Kubernetes NetworkPolicy politikalarını aktif etmediği için, birden fazla node'a sahip olan bu Cluster sistemini detaylıca kontrol edebilecek Calico'yu kullanmaya karar verdim.

Görevi tamamlarken zamanımı alan bir diğer sorun da Calico'nun kurulumunu basitçe yapmayı bulmaktı.

Calico'nun websitesinde bulunan (https://docs.tigera.io/calico/latest/getting-started/kubernetes/quickstart) "Calico quickstart guide"ı takip ederek Calico kurmaya karar verdim. Bunun için öncelikle master node'um olan sanal makineme "kind" kurmam, "kind"ı kurabilmek için de "go" kurmam gerekti.

Buradaki sorun ise şu oldu, Calico'nun sayfasında verilen config.yaml dosyası üç sanal makineyi üç node olarak kullanmıyordu. Bunun yerine bir sanal makinenin içinde üç node kuruyordu. 

Calico'nun sağladığı config.yaml dosyasını değiştirerek devam etmeye karar verdim. Değiştirebilmek için şöyle bir plan hazırladım:
- calico.yaml dosyasını Vagrantfile’ın bulunduğu klasöre indir,
- calico.yaml dosya içeriğini düzenle,
- VM içine vagrant ssh ile girip /vagrant/calico.yaml yolunu kullan (veya scp komutuyla sanal makinenin içine kopyala)
- kubectl apply yap.

Bu plan sırasında aksaklıklar yaşadıktan sonra daha detaylı araştırma yapıp aşağıdaki komutları kullanan bir Calico kurulumu buldum:<br />
- "kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/tigera-operator.yaml"<br />
- "curl https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/custom-resources.yaml -O"<br />
- "sed -i 's/cidr: 192\.168\.0\.0\/16/cidr: 10.10.0.0\/16/g' custom-resources.yaml"<br />
- "kubectl create -f custom-resources.yaml"<br />

Bu sorunu da bulduğum Calico kurulumu ile çözmüş oldum.

![image](https://github.com/user-attachments/assets/bee62574-37f3-4bca-8d74-19dd89611ba9)<br /><br />
Daha ileri aşamada Calico kullanarak yaptığım ağ ayarlamalarında; nonamens namespace'indeki bir poddan, codegen namespace'indeki bir poda ping atıldığında cevap alınamaması için projeme deny-nonamens-icmp-to-codegen.yaml dosyasını ekledim. Dosya içerisinde, podlar arasında izin verilmeyen protokol olarak ICMP'i ekledim.

### Helm Chart 
Projemde:<br />
deploy-with-helm.sh – bu dosya Helm ile deployment yapıyor.<br />
codegen-chart/ – Helm chart'ını, values.yaml dosyasını ve diğer yaml dosyalarını barındıran templates klasörünü içeriyor.<br />

### Önemli Not

Uygulamanın geliştirilmesi sırasında Ollama servisi pod'ları ayakta ve çalışıyor olmasına rağmen, sistemin kalanı ile iletişim kuramaması sorunu yaşadım.

Bu yüzden, sitede "Generate Code" butonuna bastıldığında 
"# An error occurred: 404 Client Error: Not Found for url: http://ollama-service:11434/api/generate"
şeklinde hata aldım. 

Bunu atlatabilmek için doğru Ollama modelini kullandığımdan emin olmaya çalıştım. 
Kullandığım Llama 2 modelinin doğru şekilde indirili olduğundan ve modele de Ollama sistemine de doğru şekilde erişilmeye çalışıldığından emin olmaya çalıştım. 

"kubectl get pods" ve "kubectl get pvc" komutlarını kullanarak Ollama'nın da bulunduğu pod'u kontrol ettiğimde sorunsuz çalıştığını gördüm.

Bu sorunu, Ollama modelini Llama 3.2 ile Llama 2 arasında değiştirmek de dahil olmak üzere farklı yöntemlerle çözmeye çalıştım fakat işe yaramadı. 
Bu yüzden erişeceğiniz web sitesi, bahsettiğim şekilde hata verme ihtimaline sahiptir. 

## Overview

This application provides a web interface where users enter a prompt. 
Then, get Python code regarding the prompt that extends the Job class and a title for the code generated by the Llama.

### Features

Project is done using Flask, Llama 2 of Ollama, Minikube, Kubectl and DockerHub.

DockerHub, as wanted in the mail, can be found at elifdenizgoztok/code-generator repository in DockerHub.
https://hub.docker.com/r/elifdenizgoztok/code-generator

If you cannot find the DockerHub repository, please reach out to me. 

## Architecture

Web UI (Browser) - Flask API Server - Ollama (Llama 2)

The application has:
- A web interface
- A Flask web server serving the frontend and API
- Ollama running locally or in a container to host Llama 2

## Prerequisites

To run the app locally or deploy it, you'll need:
- Docker and Docker Compose
- Minikube
- kubectl
- Ollama installed (if running locally without Docker)

## Getting Started

### Local Development

1. Clone the repository:
   git clone <repository-url>
   cd ai-code-generator

2. Create a `.env` file based on the example:
   cp env.example .env

3. Choose how you want to run it:

   **Option 1: Using Docker Compose**
   docker-compose up --build

   **Option 2: Running locally**
    Make sure Ollama is installed and running
   ollama pull llama2

    Install Python dependencies
   pip install -r requirements.txt

    Start the Flask app
   python app.py

4. Open your browser and go to: [http://localhost:8080](http://localhost:8080)

### Kubernetes Deployment with Minikube

#### Automated Deployment

To make setup easier, I added scripts (`deploy.bat` for Windows and `deploy.sh` for Linux/macOS).  
They automatically check for Minikube and kubectl, build and load the Docker image into Minikube, deploy Ollama, and display the service URL.

#### Manual Deployment

1. Start Minikube:
   minikube start

2. Build and load the Docker image:
   docker build -t code-generator:latest .
   minikube image load code-generator:latest

3. Deploy the services:
   kubectl apply -f k8s/ollama.yaml
   kubectl apply -f k8s/code-generator.yaml

4. Get the service URL:
   minikube service code-generator-service --url

## API Endpoints

- `GET /` – Loads the web interface
- `POST /generate` – Generates Python code based on a user prompt
  - Request body: `{ "prompt": "Your prompt here" }`
  - Response: `{ "title": "Generated title", "code": "Generated code" }`

## Implementation Details

### Project Structure

── app.py                     # Main Flask app
── llm_client.py               # Ollama client for Llama 2
── templates/                  # HTML templates
── index.html              # Web UI
── s4e/                        # Project package
   ── __init__.py
   ── config.py
   ── task.py
   ── job.py                  # Base Job class
── k8s/                        # Kubernetes configs
   ── code-generator.yaml
   ── ollama.yaml
── deploy.sh                   # Deployment script for Linux/macOS
── deploy.bat                  # Deployment script for Windows
── Dockerfile                  # Docker build file
── requirements.txt            # Python dependencies
── README.md                   


## How It Works

1. The user enters a prompt on the web page.
2. The Flask server sends the prompt to the LLM client.
3. The client adds a system prompt with a `Job` class template and forwards it to Llama 2.
4. Llama generates a Python class extending the `Job` class.
5. The server extracts the generated code and title from the response.
6. The result is shown on the web interface.

## License

MIT License
