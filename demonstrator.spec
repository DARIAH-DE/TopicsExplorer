# -*- mode: python -*-

block_cipher = None


a = Analysis(['demonstrator.py'],
             pathex=['/Users/severin/Desktop/Topics/demonstrator'],
             binaries=[],
             datas=[('static', 'static'), ('templates', 'templates')],
             hiddenimports=[],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='demonstrator',
          debug=False,
          strip=False,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='demonstrator.app',
             icon=None,
             bundle_identifier=None)
