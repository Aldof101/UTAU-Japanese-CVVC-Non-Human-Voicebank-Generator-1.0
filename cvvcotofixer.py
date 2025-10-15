# Script to fix oto.ini file for Japanese voicebank
# Fixes incorrect romaji notations and corresponding hiragana characters

import os
import re

def detect_encoding(file_path):
    """
    Detect file encoding by trying common encodings
    """
    encodings = ['shift_jis', 'cp932', 'euc_jp', 'utf-8', 'gbk', 'big5']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    
    # If no encoding works, return None
    return None

def create_romaji_to_hiragana_map():
    """
    Create mapping from romaji to hiragana characters
    """
    mapping = {
        # Basic vowels
        'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
        
        # K line
        'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
        'kya': 'きゃ', 'kyu': 'きゅ', 'kye': 'きぇ', 'kyo': 'きょ',
        
        # S line  
        'sa': 'さ', 'si': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
        'sha': 'しゃ', 'shi': 'し', 'shu': 'しゅ', 'she': 'しぇ', 'sho': 'しょ',
        'sya': 'しゃ', 'syi': 'しぃ', 'syu': 'しゅ', 'sye': 'しぇ', 'syo': 'しょ',
        
        # T line
        'ta': 'た', 'ti': 'ち', 'tu': 'つ', 'te': 'て', 'to': 'と',
        'tsa': 'つぁ', 'tsi': 'つぃ', 'tsu': 'つ', 'tse': 'つぇ', 'tso': 'つぉ',
        'cha': 'ちゃ', 'chi': 'ち', 'chu': 'ちゅ', 'che': 'ちぇ', 'cho': 'ちょ',
        'tya': 'ちゃ', 'tyi': 'ちぃ', 'tyu': 'ちゅ', 'tye': 'ちぇ', 'tyo': 'ちょ',
        
        # N line
        'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
        'nya': 'にゃ', 'nyi': 'にぃ', 'nyu': 'にゅ', 'nye': 'にぇ', 'nyo': 'にょ',
        
        # H line
        'ha': 'は', 'hi': 'ひ', 'hu': 'ふ', 'he': 'へ', 'ho': 'ほ',
        'hya': 'ひゃ', 'hyi': 'ひぃ', 'hyu': 'ひゅ', 'hye': 'ひぇ', 'hyo': 'ひょ',
        'fa': 'ふぁ', 'fi': 'ふぃ', 'fu': 'ふ', 'fe': 'ふぇ', 'fo': 'ふぉ',
        'fya': 'ふゃ', 'fyi': 'ふぃ', 'fyu': 'ふゅ', 'fye': 'ふぇ', 'fyo': 'ふょ',
        
        # M line
        'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
        'mya': 'みゃ', 'myi': 'みぃ', 'myu': 'みゅ', 'mye': 'みぇ', 'myo': 'みょ',
        
        # Y line
        'ya': 'や', 'yi': 'い', 'yu': 'ゆ', 'ye': 'いぇ', 'yo': 'よ',
        
        # R line
        'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
        'rya': 'りゃ', 'ryi': 'りぃ', 'ryu': 'りゅ', 'rye': 'りぇ', 'ryo': 'りょ',
        'rwa': 'るぁ', 'rwi': 'るぃ', 'rwu': 'るぅ', 'rwe': 'るぇ', 'rwo': 'るぉ',
        
        # W line
        'wa': 'わ', 'wi': 'うぃ', 'wu': 'う', 'we': 'うぇ', 'wo': 'を',
        
        # G line
        'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
        'gya': 'ぎゃ', 'gyi': 'ぎぃ', 'gyu': 'ぎゅ', 'gye': 'ぎぇ', 'gyo': 'ぎょ',
        'gwa': 'ぐぁ', 'gwi': 'ぐぃ', 'gwu': 'ぐぅ', 'gwe': 'ぐぇ', 'gwo': 'ぐぉ',
        
        # Z line
        'za': 'ざ', 'zi': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
        'dza': 'づぁ', 'dzi': 'づぃ', 'dzu': 'づ', 'dze': 'づぇ', 'dzo': 'づぉ',
        
        # D line
        'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
        'dya': 'ぢゃ', 'dyi': 'ぢぃ', 'dyu': 'ぢゅ', 'dye': 'ぢぇ', 'dyo': 'ぢょ',
        
        # B line - FIXED: should be 'ba', not 'va'
        'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
        'bya': 'びゃ', 'byi': 'びぃ', 'byu': 'びゅ', 'bye': 'びぇ', 'byo': 'びょ',
        
        # P line
        'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
        'pya': 'ぴゃ', 'pyi': 'ぴぃ', 'pyu': 'ぴゅ', 'pye': 'ぴぇ', 'pyo': 'ぴょ',
        
        # J line - FIXED: should be 'ja', not 'jya'
        'ja': 'じゃ', 'ji': 'じ', 'ju': 'じゅ', 'je': 'じぇ', 'jo': 'じょ',
        'jya': 'じゃ', 'jyi': 'じぃ', 'jyu': 'じゅ', 'jye': 'じぇ', 'jyo': 'じょ',
        'dja': 'ぢゃ', 'dji': 'ぢぃ', 'dju': 'ぢゅ', 'dje': 'ぢぇ', 'djo': 'ぢょ',
        
        # Special cases
        'n': 'ん', '-': '・'
    }
    return mapping

def create_romaji_correction_map():
    """
    Create mapping to correct incorrect romaji notations
    """
    corrections = {
        # Fix va/vi/vu/ve/vo to ba/bi/bu/be/bo
        'va': 'ba', 'vi': 'bi', 'vu': 'bu', 've': 'be', 'vo': 'bo',
        # Fix jya/jyi/jyu/jye/jyo to ja/ji/ju/je/jo
        'jya': 'ja', 'jyi': 'ji', 'jyu': 'ju', 'jye': 'je', 'jyo': 'jo',
        # Fix other potential issues
        'chy': 'ch', 'shy': 'sh'
    }
    return corrections

def extract_base_romaji(romaji_string):
    """
    Extract base romaji from string that may contain numbers or other suffixes
    e.g., 'jya1' -> 'jya', 'a b' -> 'a'
    """
    # Remove numbers and spaces, split by space and take first part
    base = romaji_string.split()[0] if ' ' in romaji_string else romaji_string
    # Remove trailing numbers
    base = re.sub(r'\d+$', '', base)
    return base

def correct_romaji(romaji_string, correction_map):
    """
    Correct romaji notation using correction map
    """
    base_romaji = extract_base_romaji(romaji_string)
    
    # Check if base romaji needs correction
    if base_romaji in correction_map:
        corrected_base = correction_map[base_romaji]
        # Replace the base part while preserving numbers and other parts
        if ' ' in romaji_string:
            parts = romaji_string.split()
            parts[0] = corrected_base + romaji_string[len(base_romaji):len(parts[0])]
            return ' '.join(parts)
        else:
            return corrected_base + romaji_string[len(base_romaji):]
    
    return romaji_string

def is_hiragana_garbled(text):
    """
    Check if text contains garbled hiragana characters (likely mojibake)
    """
    # Common patterns for garbled Japanese text
    garbled_patterns = ['•Ű', '§', 'ů', '™', '®', '¶', 'Ę']
    return any(pattern in text for pattern in garbled_patterns)

def fix_oto_line(line, romaji_map, correction_map):
    """
    Fix a single line from oto.ini file
    """
    if '=' not in line:
        return line
    
    filename, params = line.split('=', 1)
    param_parts = params.split(',')
    
    if len(param_parts) < 6:
        return line
    
    romaji_field = param_parts[0]
    
    # Check if this is a romaji line or hiragana line
    if is_hiragana_garbled(romaji_field):
        # This is a hiragana line - we need to find the correct hiragana
        # Look at the romaji from previous context or filename to determine correct hiragana
        base_romaji = extract_base_romaji(romaji_field)
        corrected_romaji = correct_romaji(base_romaji, correction_map)
        
        if corrected_romaji in romaji_map:
            param_parts[0] = romaji_map[corrected_romaji]
        else:
            # If we can't map it, try to extract from filename
            for known_romaji in romaji_map:
                if known_romaji in filename.lower():
                    param_parts[0] = romaji_map[known_romaji]
                    break
    
    else:
        # This is a romaji line - correct the romaji
        corrected_romaji = correct_romaji(romaji_field, correction_map)
        param_parts[0] = corrected_romaji
    
    # Reconstruct the line
    fixed_params = ','.join(param_parts)
    return f"{filename}={fixed_params}"

def fix_oto_file(file_path):
    """
    Main function to fix oto.ini file
    """
    romaji_map = create_romaji_to_hiragana_map()
    correction_map = create_romaji_correction_map()
    
    # Detect file encoding
    encoding = detect_encoding(file_path)
    if encoding is None:
        print("Error: Could not detect file encoding. Trying with error handling...")
        encoding = 'shift_jis'  # Default to Shift-JIS for Japanese files
    
    print(f"Detected encoding: {encoding}")
    
    # Read the original file with detected encoding
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Process each line
    fixed_lines = []
    for line in lines:
        line = line.strip()
        if line:
            fixed_line = fix_oto_line(line, romaji_map, correction_map)
            fixed_lines.append(fixed_line)
    
    # Create backup and write fixed file
    backup_path = file_path + '.bak'
    try:
        os.rename(file_path, backup_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return
    
    # Write fixed file with UTF-8 encoding
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
    except Exception as e:
        print(f"Error writing fixed file: {e}")
        # Restore backup if write fails
        try:
            os.rename(backup_path, file_path)
            print("Restored original file due to write error")
        except:
            pass
        return
    
    print(f"Fixed oto.ini file. Backup created at: {backup_path}")
    print(f"Fixed {len(fixed_lines)} lines.")

# Main execution
if __name__ == "__main__":
    oto_file_path = r"this\is\YOUR\oto.ini"
    
    if os.path.exists(oto_file_path):
        fix_oto_file(oto_file_path)
    else:
        print(f"File not found: {oto_file_path}")
        print("Please check the file path and try again.")