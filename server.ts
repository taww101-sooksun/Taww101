import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';

const app = express();
const PORT = 3000;

app.use(express.json());

function getGeminiClient(): GoogleGenAI | null {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return null;
  return new GoogleGenAI({ apiKey });
}

const CANDIDATE_MODELS = ['gemini-3.7-flash', 'gemini-2.5-flash', 'gemini-flash-latest'];

async function generateContentWithRetry(
  ai: GoogleGenAI,
  params: { contents: string; config?: any }
): Promise<string | null> {
  for (const model of CANDIDATE_MODELS) {
    try {
      const response = await ai.models.generateContent({
        model,
        contents: params.contents,
        config: params.config,
      });
      if (response && response.text) {
        return response.text;
      }
    } catch (err: any) {
      console.warn(`[Gemini API] Model ${model} temporary error:`, err?.message);
    }
  }
  return null;
}

// Health Check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    geminiConfigured: !!process.env.GEMINI_API_KEY,
    timestamp: new Date().toISOString()
  });
});

// AI Songwriter Lyricist
app.post('/api/ai/compose-lyrics', async (req, res) => {
  try {
    const { topic, genre = 'cyber_synthwave', mood = 'energetic', language = 'th' } = req.body;
    const ai = getGeminiClient();

    if (!ai) {
      return res.json({
        success: true,
        lyrics: `[Verse 1]\nเสียงดนตรีดังในค่ำคืนนี้ (${topic})\nแสงไฟนีออนส่องประกายสว่างไสว\n\n[Chorus]\nให้เสียงเพลงพาเราก้าวไปข้างหน้า\nจังหวะหัวใจเต้นพร้อมท่วงทำนอง`,
        topic
      });
    }

    const prompt = `แต่งเนื้อเพลงแนว ${genre} อารมณ์ ${mood} ธีมหัวข้อเรื่อง: "${topic}" เป็นภาษา ${language === 'th' ? 'ไทย' : 'อังกฤษ'} โดยแบ่งท่อน [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge], [Outro] ให้ไพเราะและร้องง่าย`;

    const generatedText = await generateContentWithRetry(ai, { contents: prompt }) || `[Chorus]\nเสียงเพลงของ ${topic} ดังก้องในใจ`;

    res.json({ success: true, lyrics: generatedText, topic });
  } catch (error) {
    res.json({ success: true, lyrics: `[Chorus]\nเสียงเพลงดังก้องในใจ (${req.body.topic || 'Beat'})`, topic: req.body.topic });
  }
});

// AI Avatar Outfit Matcher
app.post('/api/ai/match-avatar-style', async (req, res) => {
  try {
    const { genre = 'cyber_synthwave', mood = 'energetic' } = req.body;
    const ai = getGeminiClient();

    if (!ai) {
      return res.json({
        success: true,
        outfit: 'cyber_jacket',
        pose: 'dynamic_singing',
        lighting: 'neon_cyan_magenta',
        reasonTh: 'จับคู่สไตล์ตามแนวเพลงอัตโนมัติ'
      });
    }

    const prompt = `Suggest a 3D avatar stage costume and lighting for genre "${genre}" and mood "${mood}". Respond in JSON format: {"outfit": "cyber_jacket", "pose": "dynamic_singing", "lighting": "neon_cyan_magenta", "reasonTh": "คำอธิบายสั้นๆ"}`;

    const textResponse = await generateContentWithRetry(ai, {
      contents: prompt,
      config: { responseMimeType: 'application/json' }
    });

    let result = {
      outfit: 'cyber_jacket',
      pose: 'dynamic_singing',
      lighting: 'neon_cyan_magenta',
      reasonTh: 'วิเคราะห์สไตล์เพลงอัตโนมัติ'
    };

    if (textResponse) {
      try {
        result = { ...result, ...JSON.parse(textResponse) };
      } catch {}
    }

    res.json({ success: true, ...result });
  } catch (error) {
    res.json({
      success: true,
      outfit: 'cyber_jacket',
      pose: 'dynamic_singing',
      lighting: 'neon_cyan_magenta',
      reasonTh: 'จับคู่สไตล์พื้นฐานตามแนวเพลง'
    });
  }
});

async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
