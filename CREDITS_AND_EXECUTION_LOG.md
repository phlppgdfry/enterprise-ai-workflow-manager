# ⏱️ Credits & Uitvoeringslogboek

Dit document houdt de actuele status bij van AI-credits, sessie-resets en uitvoeringsstrategieën om te zorgen dat ontwikkeling altijd reproduceerbaar en kostenbewust blijft.

---

## 1. Actuele Status & Resettijden (Gemeten: 7 november 2026, 03:48 CET)

| Systeem / Model | Status | Huidig verbruik | Resettijd | Actie / Strategie |
|---|---|---|---|---|
| **Claude Code (5-uurs sessie)** | ⚠️ Kritiek | **92%** | **06:29:59 CET** (05:29:59 UTC) | Zuinig werken, geen loze iteraties; hervatten na reset |
| **Claude Code (7-daagse limiet)** | 🟢 Normaal | **71%** | **9 nov 2026, 19:59 CET** | Binnen budget; zware taken clusteren |
| **Claude Extra Usage Credits** | ⚪ Uit | € 0,00 | N.v.t. (uitgeschakeld) | Geen onverwachte kosten |
| **Replit MCP Server** | 🟢 Actief | Verbonden via OAuth | Maandelijkse billing cyclus | Alleen gerichte calls via Replit Agent |
| **Antigravity / Gemini CLI** | 🟢 Actief | Volledig operationeel | Doorlopend | Primaire orchestrator voor lokale codebouw |
| **GitHub CLI (`gh`)** | 🟢 Actief | Onbeperkt | N.v.t. | Directe versiebeheer en synchronisatie |

---

## 2. Replit Credit-optimalisatiestrategie

Replit Agent verbruikt cloud-credits bij elke generatie via `create_app_from_prompt` of `update_app_using_prompt`. Om te voorkomen dat credits voortijdig opraken en tegelijkertijd een **Level 4 Advanced Builder**-beoordeling te behalen:

1. **Lokaal steigeren en specificeren:**  
   Architectuur, datamodellen, businesslogica en test-suites worden lokaal ontworpen en opgebouwd (zonder Replit credits te verspillen).
2. **Gerichte import en validatie via Replit:**  
   Het project wordt via GitHub geïmporteerd of via de Replit MCP API geoptimaliseerd, waardoor de Replit Agent hoogwaardige context krijgt (Level 2 & 3 criteria).
3. **Deployment & Cloud Evaluatie:**  
   Replit Agent wordt ingezet voor cloud-configuratie, PostgreSQL-koppeling en live publishing (Level 4 criterium: productierijpe release).
4. **Hervatten bij Reset:**  
   Mocht Claude Code of Replit tegen een limiet aanlopen, dan ligt alle code en documentatie al commit-klaar in GitHub. De volgende sessie start direct bij de specifieke openstaande proef.
