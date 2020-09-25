setImmediate(function() {
	Java.perform(function() {
		var hook = Java.use("android.telephony.SmsManager");
		hook.sendTextMessage.overload('java.lang.String', 'java.lang.String', 'java.lang.String', 'android.app.PendingIntent', 'android.app.PendingIntent').implementation = function(arg_0, arg_1, arg_2, arg_3, arg_4){
			console.log('[*] Hello world');
			result = this.sendTextMessage(arg_0, arg_1, arg_2, arg_3, arg_4);
			// logmessage = 'android.telephony.SmsManager,sendTextMessage\n' + 'arg_0: ' + arg_0.toString() + '\n' + 'arg_1: ' + arg_1.toString() + '\n' + 'arg_2: ' + arg_2.toString() + '\n' + 'arg_3: ' + arg_3.toString() + '\n' + 'arg_4: ' + arg_4.toString() + '\n' + ' => ' + result;
			// console.log('\n[*]Code: ' + logmessage + '\n[*]Stacktrace:\n');
			thread = Java.use('java.lang.Thread').currentThread().getStackTrace();
			for (var i = 0; i <= thread.length - 1; i++) {
			    send(thread[i].getClassName() + '.' + thread[i].getMethodName() + ' at ' + thread[i].getFileName() + ' line ' + thread[i].getLineNumber().toString());
			}
			return result;
			//show hello world whenever android.app.ActivityManager.getRunningAppProcesses() is called
			
		};
		
	});
})



result = this.onCreate(arg_0);
log = '[*]Stack trace:\n';
thread = Java.use('java.lang.Thread').currentThread().getStackTrace();
for (var i = 0; i <= thread.length - 1; i++) {
    log += thread[i].getClassName() + '.' + thread[i].getMethodName() + ' at ' + thread[i].getFileName() + ' line ' + thread[i].getLineNumber().toString();
}
send(log);
return result;