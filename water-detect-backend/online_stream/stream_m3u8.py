class stream_m3u8:
    def __init__(self, file_path, buffer_file=6):
        self.file_path = file_path
        self.ts_files = []
        self.target_duration = 20
        self.media_sequence = 0
        self.buffer_file = buffer_file
        self.eof = False
    def push(self, ts_file, duration):
        self.ts_files.append((ts_file, duration))
        if len(self.ts_files) > self.buffer_file:
            self.ts_files = self.ts_files[-self.buffer_file:]
            self.media_sequence += 1
    def done(self):
        self.eof = True
    def write(self):
        try:
            with open(self.file_path, 'w') as f:
                f.write('#EXTM3U\n')
                f.write('#EXT-X-VERSION:3\n')
                f.write(f'#EXT-X-TARGETDURATION:{self.target_duration}\n')
                f.write(f'#EXT-X-MEDIA-SEQUENCE:{self.media_sequence}\n')
                for ts_file, duration in self.ts_files:
                    f.write(f'#EXTINF:{duration},\n')
                    f.write(f'{ts_file}\n')
                if self.eof:
                    f.write('#EXT-X-ENDLIST:ENDLIST\n')
        except Exception as e:
            print(f"error when write stream_m3u8: {e}")


# 示例用法
if __name__ == "__main__":
    m3u8 = stream_m3u8('output.m3u8')
    m3u8.push('stream_remote8.ts', 16.683333)
    m3u8.push('stream_remote9.ts', 8.341667)
    m3u8.push('stream_remote10.ts', 8.341667)
    m3u8.push('stream_remote11.ts', 8.341667)
    m3u8.push('stream_remote12.ts', 8.341667)
    m3u8.push('stream_remote13.ts', 15.582233)
    m3u8.push('stream_remote14.ts', 15.582233)
    m3u8.push('stream_remote15.ts', 15.582233)
    m3u8.write()
