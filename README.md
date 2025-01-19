  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }

    .typing-effect {
      font-size: 24px;
      color: #333;
      white-space: nowrap;
      overflow: hidden;
      border-right: 3px solid #333;
      width: 0;
      animation: typing 4s steps(30, end), blink 0.6s step-end infinite;
    }

    @keyframes typing {
      from { width: 0; }
      to { width: 100%; }
    }

    @keyframes blink {
      from { border-color: transparent; }
      to { border-color: #333; }
    }
  </style>
<body>
  <div class="typing-effect">
    Welcome to my personal repository!
  </div>
</body>
