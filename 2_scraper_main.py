from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import pandas as pd
import time, random, re, os
from urllib.parse import quote

try:
    from playwright_stealth import stealth_sync
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False
    print("playwright-stealth tidak terinstall. Fingerprint browser bisa lebih mudah terdeteksi.")
    print("Install opsional: pip install playwright-stealth\n")


# Konfigurasi akun dan parameter scraping
EMAIL        = 'masukkan email dummy / utama untuk scrappinhg'
PASSWORD     = 'masukkan pass akun'
LOCATION     = 'WorldWide'
TARGET_JOBS  = 50
HEADLESS     = False
SESSION_FILE = 'linkedin_session.json'

KEYWORDS = [
    '"Back End Developer"',
    '"Front End Developer"',
    '"FullStack Developer"',
    '"Web Developer"',
    '"Android Developer"',
    '"iOS Developer"',
    '"Mobile Developer"',
    '"Flutter Developer"',
    '"React Native Developer"',
    '"Golang Developer"',
    '"Java Developer"',
    '"PHP Developer"',
    '"Python Developer"',
    '"NodeJS Developer"',
    '".NET Developer"',
    '"QA Automation Engineer"',
    '"QA Manual-Tester"',
    '"Software Quality Assurance"',
    '"QA Analyst"',
    '"Data Analyst"',
    '"Data Engineer"',
    '"Data Scientist"',
    '"Business Intelligence Analyst"',
    '"Database Administrator"',
    '"ERP Consultant"',
    '"SAP Consultant"',
    '"Salesforce Developer"',
    '"DevOps Engineer"',
    '"Cloud Engineer"',
    '"System Administrator"',
    '"Network Engineer"',
    '"IT Infrastructure Engineer"',
    '"System Engineer"',
    '"Linux Administrator"',
    '"Cyber Security Analyst"',
    '"Information Security Engineer"',
    '"Penetration Tester"',
    '"IT Security Officer"',
    '"UI/UX Designer"',
    '"Product Manager"',
    '"Product Owner"',
    '"Scrum Master"',
    '"IT Business Analyst"',
    '"System Analyst"',
    '"IT Project Manager"',
    '"IT-Support Staff"',
    '"Technical Support-Engineer"',
    '"Helpdesk IT"',
    '"Application Support"',
    '"IT Network-Support"',
    '"IT Operations"',
    '"Unity Developer"',
    '"Unreal Engine-Developer"',
    '"Game Programmer"',
    '"Game Artist"',
    '"Game Designer"',
    '"Machine Learning Engineer"',
    '"Artificial Intelligence Engineer"',
    '"NLP Engineer"',
    '"Computer Vision Engineer"',
    '"Prompt Engineer"',
    '"C++ Developer"',
    '"Ruby on Rails Developer"',
    '"Rust Developer"',
    '"Scala Developer"',
    '"Blockchain Developer"',
    '"Smart Contract Developer"',
    '"Embedded Software Engineer"',
    '"Firmware Engineer"',
    '"AR/VR Developer"',
    '"Data Architect"',
    '"Big Data Engineer"',
    '"MLOps Engineer"',
    '"Analytics Engineer"',
    '"ETL Developer"',
    '"Site Reliability Engineer"',
    '"Release Engineer"',
    '"AWS Solutions Architect"',
    '"Azure Cloud Engineer"',
    '"Platform Engineer"',
    '"Virtualization Engineer"',
    '"SOC Analyst"',
    '"Ethical Hacker"',
    '"Application Security Engineer"',
    '"Cloud Security Engineer"',
    '"IAM Engineer"',
    '"UX Researcher"',
    '"Interaction Designer"',
    '"Technical Writer"',
    '"Information Architect"',
    '"Chief Technology Officer"',
    '"Chief Information Officer"',
    '"VP of Engineering"',
    '"Engineering Manager"',
    '"Software Development Manager"',
    '"IT Director"',
    '"Solutions Architect"',
    '"Pre-Sales Engineer"',
    '"Technical Account Manager"',
    '"IT Auditor"',
    '"IT Consultant"',
    '"Network Administrator"',
    '"NOC Engineer"',
    '"Desktop Support Technician"',
    '"IT Asset Manager"',
]

# Daftar skill teknis yang akan dicari dalam deskripsi lowongan
TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Ruby", "Go (Golang)", "Rust",
    "Swift", "Kotlin", "PHP", "R", "MATLAB", "Objective-C", "Scala", "Perl", "Haskell", "Lua",
    "Dart", "Julia", "Cobol", "Fortran", "Lisp", "Prolog", "Assembly Language", "SQL", "HTML5", "CSS3",
    "F#", "Clojure", "Elixir", "Erlang", "Groovy", "VBScript", "Shell Scripting", "Bash", "PowerShell", "Solidity",
    "React.js", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "Gatsby", "Bootstrap", "Tailwind CSS",
    "Material-UI (MUI)", "Chakra UI", "Ant Design", "Bulma", "Foundation", "Semantic UI", "Redux", "MobX",
    "Vuex", "Zustand", "RxJS", "Webpack", "Vite", "Babel", "Parcel", "Rollup", "DOM Manipulation",
    "WebAssembly (Wasm)", "Service Workers", "Progressive Web Apps (PWA)", "WebSockets", "Canvas API", "WebGL",
    "Micro-Frontends", "Storybook", "Framer Motion", "Three.js", "D3.js", "Chart.js", "Lottie", "Sass/SCSS",
    "Less", "Stylus", "PostCSS", "Responsive Web Design", "Cross-Browser Compatibility", "Web Accessibility (WCAG)",
    "Node.js", "Express.js", "NestJS", "Django", "Flask", "FastAPI", "Spring Boot", "Hibernate", "ASP.NET Core",
    "Laravel", "CodeIgniter", "Symfony", "Ruby on Rails", "Sinatra", "Phoenix", "Fiber", "Gin", "Echo",
    "GraphQL", "RESTful APIs", "gRPC", "SOAP", "Microservices Architecture", "Serverless Architecture",
    "RabbitMQ", "Apache Kafka", "ActiveMQ", "ZeroMQ", "Celery", "Redis Pub/Sub", "Socket.io",
    "React Native", "Flutter", "Android SDK", "iOS SDK", "Xamarin", "Ionic", "Cordova", "SwiftUI",
    "Jetpack Compose", "React Navigation", "CoreData", "Room Database", "Retrofit", "Alamofire",
    "Mobile App Profiling", "App Store Optimization (ASO)", "Mobile UI/UX", "Push Notifications (FCM/APNs)",
    "MySQL", "PostgreSQL", "SQLite", "Oracle Database", "Microsoft SQL Server", "MariaDB", "IBM DB2",
    "MongoDB", "Couchbase", "CouchDB", "Cassandra", "DynamoDB", "Redis", "Memcached", "Elasticsearch",
    "Neo4j", "ArangoDB", "Firebase Realtime Database", "Cloud Firestore", "Supabase", "InfluxDB", "TimescaleDB",
    "ClickHouse", "Snowflake", "Amazon Redshift", "Google BigQuery", "Teradata", "HBase", "RavenDB",
    "Data Modeling", "Database Normalization", "ACID Properties", "CAP Theorem", "Query Optimization",
    "Amazon Web Services (AWS)", "AWS EC2", "AWS S3", "AWS Lambda", "AWS RDS", "AWS VPC", "AWS IAM",
    "AWS CloudFormation", "AWS ECS", "AWS EKS", "Microsoft Azure", "Azure Virtual Machines", "Azure Functions",
    "Azure Cosmos DB", "Azure App Service", "Azure DevOps", "Google Cloud Platform (GCP)", "Google Compute Engine",
    "Google Kubernetes Engine (GKE)", "Google Cloud Storage", "Cloud Run", "Heroku", "DigitalOcean",
    "Linode", "Vultr", "Cloudflare", "Vercel", "Netlify", "OpenStack", "Serverless Framework",
    "Git", "GitHub", "GitLab", "Bitbucket", "Docker", "Docker Compose", "Kubernetes", "Helm", "Istio",
    "Jenkins", "GitHub Actions", "GitLab CI/CD", "Travis CI", "CircleCI", "Bamboo", "ArgoCD", "Spinnaker",
    "Ansible", "Terraform", "Puppet", "Chef", "Vagrant", "Prometheus", "Grafana", "ELK Stack (Elasticsearch, Logstash, Kibana)",
    "Datadog", "Splunk", "New Relic", "AppDynamics", "Dynatrace", "Nginx", "Apache HTTP Server", "HAProxy",
    "Traefik", "Linux System Administration", "Windows Server Administration", "Chaos Engineering", "Site Reliability Engineering (SRE)",
    "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Jupyter Notebooks", "Apache Spark",
    "Apache Hadoop", "Apache Flink", "Apache Airflow", "dbt (Data Build Tool)", "Luigi", "Prefect", "Dagster",
    "Databricks", "Tableau", "Power BI", "Looker", "Metabase", "QlikView", "Data Warehousing", "Data Lakes",
    "ETL/ELT Pipelines", "Web Scraping", "BeautifulSoup", "Scrapy", "Selenium", "Puppeteer", "Data Cleansing",
    "Feature Engineering", "A/B Testing", "Statistical Analysis", "Data Mining",
    "Machine Learning", "Deep Learning", "Natural Language Processing (NLP)", "Computer Vision", "Reinforcement Learning",
    "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "Hugging Face Transformers", "OpenCV", "NLTK", "SpaCy",
    "YOLO", "XGBoost", "LightGBM", "CatBoost", "Generative AI", "Large Language Models (LLMs)", "Prompt Engineering",
    "RAG (Retrieval-Augmented Generation)", "LangChain", "LlamaIndex", "MLOps", "MLflow", "KubeFlow", "Vertex AI",
    "SageMaker", "Azure Machine Learning", "Speech Recognition", "Text-to-Speech (TTS)", "Recommendation Systems",
    "Penetration Testing", "Ethical Hacking", "Vulnerability Assessment", "Threat Modeling", "Cryptography",
    "Identity and Access Management (IAM)", "OAuth 2.0", "OpenID Connect", "SAML", "JWT (JSON Web Tokens)",
    "SSL/TLS", "Wireshark", "Metasploit", "Nmap", "Burp Suite", "OWASP Top 10", "SIEM", "Firewall Configuration",
    "IDS/IPS", "Reverse Engineering", "Malware Analysis", "Incident Response", "Digital Forensics",
    "Data Loss Prevention (DLP)", "Zero Trust Architecture", "Endpoint Detection and Response (EDR)",
    "Cloud Security Posture Management (CSPM)", "DevSecOps", "SOC Operations", "Phishing Simulation",
    "TCP/IP Suite", "OSI Model", "DNS Management", "DHCP", "BGP", "OSPF", "VLAN/VxLAN", "VPN Protocols (IPsec, OpenVPN, WireGuard)",
    "Subnetting & IP Addressing", "Load Balancing", "Content Delivery Networks (CDN)", "SD-WAN", "Network Automation (NetDevOps)",
    "Cisco IOS", "Juniper Junos", "MikroTik", "PfSense", "Wireless Networking (Wi-Fi 6/7, WPA3)", "VoIP/SIP",
    "Figma", "Adobe XD", "Sketch", "InVision", "Zeplin", "Balsamiq", "Axure RP", "Framer",
    "Wireframing", "Rapid Prototyping", "User Research", "Usability Testing", "Information Architecture (IA)",
    "Interaction Design (IxD)", "Visual Design", "Design Systems", "Journey Mapping", "A/B Testing (Design)",
    "Unity3D", "Unreal Engine", "Godot", "CryEngine", "Game Physics", "3D Modeling", "Blender", "Maya",
    "Shaders programming (HLSL, GLSL)", "Level Design", "Game AI", "Multiplayer Networking (Photon, Mirror)",
    "AR/VR Development", "ARKit", "ARCore", "WebXR",
    "Bitcoin Architecture", "Ethereum", "Smart Contracts", "Web3.js", "Ethers.js", "Truffle", "Hardhat",
    "Ganache", "IPFS", "Hyperledger Fabric", "Consensus Algorithms (PoW, PoS, DPoS)", "DeFi Protocols",
    "NFT Development", "Zero-Knowledge Proofs (ZKP)", "Rust (Solana Smart Contracts)", "Polkadot/Substrate",
    "Object-Oriented Programming (OOP)", "Functional Programming", "Model-View-Controller (MVC)",
    "SOLID Principles", "DRY & KISS Principles", "Agile Methodology", "Scrum", "Kanban", "Extreme Programming (XP)",
    "Test-Driven Development (TDD)", "Behavior-Driven Development (BDD)", "Domain-Driven Design (DDD)",
    "Selenium Webdriver", "Cypress", "Playwright", "Jest", "Mocha", "Chai", "Jasmine", "JUnit", "PyTest",
    "Postman", "Swagger/OpenAPI", "JMeter", "Appium", "Cucumber", "Manual QA Testing", "Automated QA Testing",
    "Arduino", "Raspberry Pi", "ESP32 / ESP8266", "Microcontrollers", "Embedded C/C++", "MQTT Protocol",
    "CoAP", "Sensors and Actuators", "Programmable Logic Controllers (PLC)", "PCB Design", "Altium Designer",
    "KiCad", "Verilog / VHDL", "FPGA", "RTOS (Real-Time Operating Systems)", "Edge Computing",
    "SAP ERP", "Salesforce Administration", "Salesforce Apex", "Oracle ERP", "Microsoft Dynamics 365",
    "ServiceNow", "Workday", "Odoo", "SharePoint Development",
    "Jira", "Confluence", "Trello", "Asana", "Monday.com", "Notion", "Slack/Microsoft Teams Integrations",
    "Miro / FigJam", "Technical Writing", "API Documentation",
    "SolidJS", "HTMX", "Alpine.js", "Vuetify", "PrimeNG",
    "Prisma ORM", "TypeORM", "Entity Framework", "MuleSoft", "Spring Cloud",
    "RPA (Robotic Process Automation)", "UiPath", "Automation Anywhere", "Blue Prism", "Mendix",
    "OutSystems", "Microsoft Power Apps", "Pegasystems (Pega)",
    "WordPress Development", "Adobe Commerce (Magento)", "Shopify Development", "Liquid (Shopify)", "WooCommerce",
    "Drupal", "Sitecore",
    "Pinecone", "Milvus", "ChromaDB", "Weaviate",
    "Alteryx", "Informatica", "Talend", "Pentaho",
    "Pulumi", "AWS CDK", "HashiCorp Vault", "SonarQube", "PagerDuty",
    "Okta", "Auth0", "Palo Alto Networks", "Fortinet", "CrowdStrike",
    "Katalon Studio", "Tricentis Tosca", "BrowserStack", "Sauce Labs", "TestRail",
    "ITIL Framework", "COBIT",
    "Capacitor", "Cocos2d-x", "Phaser",
    "ABAP", "Delphi", "VBA (Visual Basic for Applications)",
]


def extract_skills(text):
    # Mencocokkan nama skill dari TECH_SKILLS dengan teks deskripsi lowongan.
    # Menggunakan regex dengan word boundary agar tidak salah deteksi substring.
    if not text:
        return ''
    text_lower = text.lower()
    found = set()
    for skill in TECH_SKILLS:
        pattern = re.escape(skill.lower())
        if re.search(r'(?<![a-z0-9])' + pattern + r'(?![a-z0-9])', text_lower):
            found.add(skill)
    return ', '.join(sorted(found))


def login_manual(page, context):
    # Membuka halaman login LinkedIn dan mengisi kredensial secara otomatis.
    # Jika muncul halaman verifikasi/captcha, user diminta menyelesaikannya manual.
    print('Membuka halaman login...')
    try:
        page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)

        if any(k in page.url for k in ['checkpoint', 'challenge', 'captcha', 'verification']):
            print('Halaman verifikasi muncul sebelum login. Selesaikan di browser, lalu tekan Enter...')
            input()
            page.wait_for_timeout(3000)
            if 'feed' in page.url or 'mynetwork' in page.url:
                print('Sudah masuk feed.')
                context.storage_state(path=SESSION_FILE)
                return True

        # Selector username dan password yang dicoba secara berurutan
        username_selectors = [
            'input#username',
            'input[name="session_key"]',
            'input[type="text"][autocomplete="username"]',
            'input[type="text"]',
            'input[autocomplete="username webauthn"]',
            'input[type="email"][autocomplete*="username"]',
            'input[type="email"]',
            'input[aria-describedby$="-info"][type="email"]',
            'input[name="username"]',
            'input[name="email"]',
            'input[data-testid="username"]',
            'input[placeholder*="Email"]',
            'input[placeholder*="username"]',
        ]
        password_selectors = [
            'input[name="session_password"]',
            'input[type="password"]',
            'input[autocomplete="current-password"]',
            'input[aria-label="Password"]',
            'input[name="password"]',
            'input[type="password"][name*="password"]',
            'form#session_key_login_ui input[type="password"]',
            'input[data-live-test-id="password-field"]',
            'input[placeholder*="Password"]',
            'input[id$="-password"]',
        ]

        print('Mencari form login...')
        username_selector = None
        password_selector = None

        start = time.time()
        while time.time() - start < 20:
            for sel in username_selectors:
                if page.query_selector(sel):
                    username_selector = sel
                    break
            if username_selector:
                break
            time.sleep(1)

        start = time.time()
        while time.time() - start < 20:
            for sel in password_selectors:
                if page.query_selector(sel):
                    password_selector = sel
                    break
            if password_selector:
                break
            time.sleep(1)

        if not username_selector:
            print(f'Field username tidak ditemukan setelah 20 detik. URL saat ini: {page.url}')
            return False

        print('Form ditemukan. Mengisi kredensial...')

        page.click(username_selector)
        page.wait_for_timeout(random.randint(500, 1000))
        page.type(username_selector, EMAIL, delay=random.randint(80, 150))
        page.wait_for_timeout(random.randint(600, 1000))

        page.click(password_selector)
        page.wait_for_timeout(random.randint(400, 800))
        page.type(password_selector, PASSWORD, delay=random.randint(80, 150))
        page.wait_for_timeout(random.randint(800, 1200))

        page.click('button[type="submit"]')
        try:
            page.wait_for_load_state('domcontentloaded', timeout=30000)
        except:
            pass
        page.wait_for_timeout(5000)

        if any(k in page.url for k in ['checkpoint', 'challenge', 'captcha', 'verification']):
            print('Verifikasi muncul setelah login. Selesaikan di browser, lalu tekan Enter...')
            input()
            page.wait_for_timeout(3000)

        context.storage_state(path=SESSION_FILE)

        if any(k in page.url for k in ['feed', 'mynetwork', 'linkedin.com/in/', 'jobs']):
            print('Login berhasil.')
            print(f'Session disimpan ke {SESSION_FILE}')
        else:
            print(f'URL setelah login: {page.url} (session tetap disimpan)')

        return True

    except Exception as e:
        print(f'Error saat login: {e}')
        return False


def ensure_login(context, page):
    # Mengecek apakah session lama masih valid. Jika tidak, jalankan login ulang.
    if os.path.exists(SESSION_FILE):
        print('Memuat session sebelumnya...')
        try:
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            if 'feed' in page.url or 'mynetwork' in page.url:
                print('Session valid, langsung masuk.')
                return True
            else:
                print('Session tidak valid, login ulang.')
                os.remove(SESSION_FILE)
        except Exception as e:
            print(f'Error memuat session: {e}')
    return login_manual(page, context)


def get_job_detail(page, job_url):
    # Membuka halaman detail lowongan, lalu mengekstrak judul, perusahaan,
    # lokasi, tipe kerja, gaji, deskripsi, dan skill dari HTML halaman.
    result = {
        'job_title':   '',
        'company':     '',
        'location':    '',
        'work_type':   '',
        'salary':      '',
        'description': '',
        'skills':      '',
    }
    try:
        page.goto(job_url, wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(random.randint(4000, 5500))

        # Klik tombol "Show more" jika ada agar deskripsi tampil penuh
        try:
            btn = page.query_selector(
                'button.show-more-less-html__button--more, '
                'button[aria-label*="more description"], '
                'button[class*="show-more-less"]'
            )
            if btn:
                btn.click()
                page.wait_for_timeout(1500)
        except:
            pass

        try:
            page.wait_for_selector(
                'div.show-more-less-html__markup, div.description__text, '
                'div.jobs-description__content, section.description, article, main',
                timeout=10000
            )
        except:
            pass

        soup = BeautifulSoup(page.content(), 'html.parser')

        h1 = soup.find('h1')
        result['job_title'] = h1.get_text(strip=True) if h1 else ''

        # Coba beberapa selector untuk nama perusahaan
        company_selectors = [
            lambda s: s.find('a', class_=lambda c: c and 'topcard__org-name-link' in ' '.join(c).lower()),
            lambda s: s.find('div', class_=lambda c: c and 'jobs-unified-top-card__company-name' in ' '.join(c).lower()),
            lambda s: s.find('span', class_=lambda c: c and 'company-name' in ' '.join(c).lower()),
            lambda s: s.find('a', class_=lambda c: c and 'company' in ' '.join(c).lower()),
        ]
        for fn in company_selectors:
            el = fn(soup)
            if el and el.get_text(strip=True):
                result['company'] = el.get_text(strip=True)
                break

        # Coba beberapa selector untuk lokasi
        location_selectors = [
            lambda s: s.find('span', class_=lambda c: c and 'topcard__flavor--bullet' in ' '.join(c).lower()),
            lambda s: s.find('span', class_=lambda c: c and 'jobs-unified-top-card__bullet' in ' '.join(c).lower()),
            lambda s: s.find('span', class_=lambda c: c and 'location' in ' '.join(c).lower()),
        ]
        for fn in location_selectors:
            el = fn(soup)
            if el and el.get_text(strip=True):
                result['location'] = el.get_text(strip=True)
                break

        # Ambil tipe pekerjaan dan gaji dari bagian kriteria lowongan
        criteria_items = soup.find_all(
            class_=lambda c: c and 'description__job-criteria-item' in ' '.join(c).lower()
        )
        for item in criteria_items:
            header = item.find(class_=lambda c: c and 'criteria-subheader' in ' '.join(c).lower())
            value  = item.find(class_=lambda c: c and 'criteria-text' in ' '.join(c).lower())
            if header and value:
                h = header.get_text(strip=True).lower()
                v = value.get_text(strip=True)
                if any(k in h for k in ['tipe', 'type', 'employment']):
                    result['work_type'] = v
                elif any(k in h for k in ['gaji', 'salary', 'compensation']):
                    result['salary'] = v

        # Ambil teks deskripsi dari elemen yang paling relevan
        desc_el = (
            soup.find('div', class_=lambda c: c and 'show-more-less-html__markup' in ' '.join(c).lower()) or
            soup.find('div', class_=lambda c: c and 'description__text' in ' '.join(c).lower()) or
            soup.find('div', class_=lambda c: c and 'jobs-description__content' in ' '.join(c).lower()) or
            soup.find('section', class_=lambda c: c and 'description' in ' '.join(c).lower()) or
            soup.find('article') or
            soup.find('main')
        )
        description = desc_el.get_text(separator=' ', strip=True) if desc_el else ''
        result['description'] = description[:800]
        result['skills']      = extract_skills(description)

    except PlaywrightTimeoutError:
        print(f'Timeout pada URL: {job_url}')
    except Exception as e:
        print(f'Error saat ambil detail: {e}')

    return result


def scroll_to_load_all_cards(page):
    # Scroll halaman daftar lowongan agar semua kartu ter-render sebelum di-parse.
    print('Scroll untuk memuat semua kartu...')
    prev_count = 0
    for attempt in range(8):
        cards = page.query_selector_all('li[data-occludable-job-id] div[data-job-id]')
        current_count = len(cards)
        if current_count == prev_count and attempt > 2:
            break
        prev_count = current_count
        page.evaluate('window.scrollBy(0, 500)')
        page.wait_for_timeout(random.randint(800, 1200))
    print(f'Kartu ter-render: {current_count}')


def scrape_keyword(page, detail_page, keyword, location, target_jobs):
    # Melakukan scraping untuk satu keyword. Iterasi halaman (offset 25 per halaman)
    # hingga jumlah lowongan yang dikumpulkan mencapai target.
    def page_url(offset):
        kw  = quote(keyword, safe='')
        loc = quote(location, safe='')
        return f'https://www.linkedin.com/jobs/search/?keywords={kw}&location={loc}&start={offset}'

    job_list  = []
    offset    = 0
    max_iter  = 20
    seen_urls = set()

    while len(job_list) < target_jobs and offset // 25 < max_iter:
        url = page_url(offset)
        print(f'Keyword "{keyword}" | Halaman offset {offset} | Terkumpul: {len(job_list)}/{target_jobs}')

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_selector('li[data-occludable-job-id]', timeout=15000)
            scroll_to_load_all_cards(page)
        except PlaywrightTimeoutError:
            print('Timeout. Kemungkinan tidak ada hasil lagi.')
            break

        soup      = BeautifulSoup(page.content(), 'html.parser')
        all_cards = soup.find_all('li', attrs={'data-occludable-job-id': True})
        cards     = [c for c in all_cards if c.find('div', attrs={'data-job-id': True})]
        print(f'Kartu ditemukan: {len(cards)}')

        if not cards:
            print('Tidak ada kartu ditemukan. Berhenti untuk keyword ini.')
            break

        for card in cards:
            if len(job_list) >= target_jobs:
                break
            try:
                link_el = card.find('a', href=lambda h: h and '/jobs/view/' in str(h))
                if not link_el or not link_el.get('href'):
                    continue

                raw_url = link_el['href'].split('?')[0]
                job_url = raw_url if raw_url.startswith('http') else 'https://www.linkedin.com' + raw_url

                if job_url in seen_urls:
                    continue

                # Ambil data preview dari kartu sebagai fallback jika detail gagal
                title_link     = card.find('a', attrs={'aria-label': True})
                title_preview  = title_link['aria-label'] if title_link else ''

                subtitle_div      = card.find('div', class_='artdeco-entity-lockup__subtitle ember-view')
                company_preview   = subtitle_div.get_text(strip=True) if subtitle_div else ''

                caption_div       = card.find('div', class_='artdeco-entity-lockup__caption ember-view')
                location_preview  = caption_div.get_text(strip=True) if caption_div else ''

                detail = get_job_detail(detail_page, job_url)

                job_data = {
                    'keyword':     keyword,
                    'job_title':   detail['job_title']  or title_preview,
                    'company':     detail['company']    or company_preview,
                    'location':    detail['location']   or location_preview,
                    'work_type':   detail['work_type'],
                    'salary':      detail['salary'],
                    'skills':      detail['skills'],
                    'job_url':     job_url,
                    'description': detail['description'],
                }

                job_list.append(job_data)
                seen_urls.add(job_url)

                skill_preview = job_data['skills'][:90] + '...' if len(job_data['skills']) > 90 else job_data['skills']
                print(f"({len(job_list):02d}) {job_data['job_title']} | {job_data['company']}")
                print(f"     Skills: {skill_preview or '(tidak ada)'}")

                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                print(f'Error pada kartu: {e}')
                continue

        offset += 25
        time.sleep(random.uniform(3.0, 5.0))

    return job_list


def save_to_csv(all_jobs, filepath):
    # Menyimpan data lowongan ke file CSV dengan kolom yang sudah ditentukan.
    kolom = ['keyword', 'job_title', 'company', 'location', 'work_type',
             'salary', 'skills', 'job_url', 'description']
    df = pd.DataFrame(all_jobs)[kolom]
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return df


def main():
    print(f'Jumlah keyword : {len(KEYWORDS)}')
    print(f'Lokasi         : {LOCATION}')
    print(f'Target per kata: {TARGET_JOBS} lowongan')
    print(f'Headless       : {HEADLESS}')
    print(f'Session file   : {SESSION_FILE if os.path.exists(SESSION_FILE) else "Belum ada"}\n')

    temp_filename = 'linkedin_scraping_temp.csv'
    if os.path.exists(temp_filename):
        try:
            os.remove(temp_filename)
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--start-maximized',
            ]
        )

        context_args = dict(
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1280, 'height': 900},
            locale='id-ID',
        )
        if os.path.exists(SESSION_FILE):
            context_args['storage_state'] = SESSION_FILE

        context = browser.new_context(**context_args)

        if HAS_STEALTH:
            stealth_sync(context)

        # Menyembunyikan tanda-tanda bahwa browser dikendalikan oleh automation
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        list_page   = context.new_page()
        detail_page = context.new_page()

        if not ensure_login(context, list_page):
            print('Tidak bisa login. Scraping dihentikan.')
            browser.close()
            return

        all_jobs       = []
        total_keywords = len(KEYWORDS)

        for i, keyword in enumerate(KEYWORDS, 1):
            print(f'\nKeyword {i}/{total_keywords}: "{keyword}"')

            try:
                jobs = scrape_keyword(list_page, detail_page, keyword, LOCATION, TARGET_JOBS)
                all_jobs.extend(jobs)
                print(f'Selesai "{keyword}": {len(jobs)} lowongan.')

                # Simpan sementara setelah setiap keyword selesai
                if jobs:
                    try:
                        save_to_csv(all_jobs, temp_filename)
                        print(f'Auto-save: {len(all_jobs)} total lowongan tersimpan di "{temp_filename}"')
                    except Exception as e:
                        print(f'Gagal auto-save: {e}')

            except Exception as e:
                print(f'Error pada keyword "{keyword}": {e}')
                print('Melanjutkan ke keyword berikutnya...')
                if all_jobs:
                    try:
                        save_to_csv(all_jobs, temp_filename)
                        print(f'Data yang sudah terkumpul ({len(all_jobs)}) tetap disimpan.')
                    except:
                        pass
                continue

        browser.close()

    if not all_jobs:
        print('\nTidak ada data yang berhasil dikumpulkan.')
        return

    timestamp      = time.strftime('%Y%m%d_%H%M%S')
    final_filename = f'linkedin_multi_{len(all_jobs)}data_{timestamp}.csv'

    # Coba simpan ke beberapa lokasi sebagai fallback
    save_paths = [
        final_filename,
        os.path.join(os.environ.get('TEMP', '.'), final_filename),
    ]
    saved = False
    for path in save_paths:
        try:
            df = save_to_csv(all_jobs, path)
            final_filename = path
            saved = True
            break
        except Exception as e:
            print(f'Gagal menyimpan ke {path}: {e}')

    if not saved:
        emergency = f'linkedin_emergency_{timestamp}.csv'
        try:
            df = save_to_csv(all_jobs, emergency)
            final_filename = emergency
            saved = True
        except Exception as e:
            print(f'Gagal menyimpan file darurat: {e}')

    total_skills = (df['skills'] != '').sum()

    print(f'\nSelesai. Total {len(all_jobs)} lowongan dari {len(KEYWORDS)} keyword.')
    if saved:
        print(f'File final    : {final_filename}')
    else:
        print('File final tidak bisa disimpan.')

    if os.path.exists(temp_filename) and temp_filename != final_filename:
        print(f'File sementara: {temp_filename} (bisa dihapus setelah final aman)')

    print(f'Skills terdeteksi pada {total_skills} lowongan.')
    print('\nPreview 5 baris pertama:')
    print(df[['keyword', 'job_title', 'company', 'location', 'skills']].head().to_string(index=False))


if __name__ == '__main__':
    main()